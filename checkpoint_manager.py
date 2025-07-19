"""
Checkpoint/Resume System for AI Video Studio
Implements state tracking for all operations with JSON-based persistence
"""

import os
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class OperationType(Enum):
    SCENARIO = "scenario"
    IMAGE = "image" 
    AUDIO = "audio"
    VIDEO = "video"
    UPLOAD = "upload"

class OperationStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class OperationState:
    operation_type: OperationType
    status: OperationStatus
    progress: float = 0.0  # 0.0 to 1.0
    current_item: int = 0
    total_items: int = 0
    output_files: List[str] = None
    error_message: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.output_files is None:
            self.output_files = []
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ProjectState:
    project_name: str
    project_path: str
    creation_time: str
    last_updated: str
    operations: Dict[str, OperationState]
    global_status: OperationStatus = OperationStatus.NOT_STARTED
    
    def __post_init__(self):
        if self.operations is None:
            self.operations = {}

class CheckpointManager:
    """Resume-from-checkpoint system for AI Video Studio"""
    
    def __init__(self, project_name: str, project_path: str = "."):
        self.project_name = project_name
        self.project_path = project_path
        self.state_file = os.path.join(project_path, f".checkpoint_{project_name}.json")
        self.project_state: Optional[ProjectState] = None
        self.load_or_create_state()
    
    def load_or_create_state(self):
        """Load existing state or create new one"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convert operations dict back to OperationState objects
                operations = {}
                for op_name, op_data in data.get('operations', {}).items():
                    op_data['operation_type'] = OperationType(op_data['operation_type'])
                    op_data['status'] = OperationStatus(op_data['status'])
                    operations[op_name] = OperationState(**op_data)
                
                data['operations'] = operations
                data['global_status'] = OperationStatus(data['global_status'])
                self.project_state = ProjectState(**data)
                
                print(f"✅ Checkpoint dosyası yüklendi: {self.state_file}")
                self._print_resume_info()
            else:
                # Create new project state
                self.project_state = ProjectState(
                    project_name=self.project_name,
                    project_path=self.project_path,
                    creation_time=datetime.now().isoformat(),
                    last_updated=datetime.now().isoformat(),
                    operations={}
                )
                print(f"🆕 Yeni proje checkpoint'i oluşturuluyor: {self.project_name}")
                
        except Exception as e:
            print(f"❌ KRITIK HATA: Checkpoint dosyası yüklenemedi: {e}")
            sys.exit(1)
    
    def _print_resume_info(self):
        """Print information about what operations can be resumed"""
        print(f"📊 Proje Durumu: {self.project_name}")
        print(f"🕐 Son güncelleme: {self.project_state.last_updated}")
        
        for op_name, op_state in self.project_state.operations.items():
            status_icon = {
                OperationStatus.NOT_STARTED: "⚪",
                OperationStatus.IN_PROGRESS: "🟡",
                OperationStatus.COMPLETED: "✅",
                OperationStatus.FAILED: "❌"
            }[op_state.status]
            
            if op_state.total_items > 0:
                progress_text = f" ({op_state.current_item}/{op_state.total_items})"
            else:
                progress_text = f" ({op_state.progress:.1%})"
                
            print(f"  {status_icon} {op_name}: {op_state.status.value}{progress_text}")
    
    def start_operation(self, operation_name: str, operation_type: OperationType, total_items: int = 0):
        """Start a new operation or resume existing one"""
        if operation_name not in self.project_state.operations:
            self.project_state.operations[operation_name] = OperationState(
                operation_type=operation_type,
                status=OperationStatus.IN_PROGRESS,
                total_items=total_items,
                start_time=datetime.now().isoformat()
            )
            print(f"🚀 Yeni operasyon başlatılıyor: {operation_name}")
        else:
            op_state = self.project_state.operations[operation_name]
            if op_state.status == OperationStatus.COMPLETED:
                print(f"✅ Operasyon zaten tamamlanmış: {operation_name}")
                return True  # Already completed
            elif op_state.status == OperationStatus.FAILED:
                print(f"🔄 Başarısız operasyon yeniden başlatılıyor: {operation_name}")
                op_state.status = OperationStatus.IN_PROGRESS
                op_state.error_message = None
            else:
                print(f"🔄 Operasyon devam ettiriliyor: {operation_name} - {op_state.current_item}/{op_state.total_items}")
        
        self.save_state()
        return False  # Not completed yet
    
    def update_progress(self, operation_name: str, current_item: int = None, progress: float = None, output_files: List[str] = None):
        """Update operation progress"""
        if operation_name not in self.project_state.operations:
            print(f"❌ KRITIK HATA: Bilinmeyen operasyon: {operation_name}")
            sys.exit(1)
        
        op_state = self.project_state.operations[operation_name]
        
        if current_item is not None:
            op_state.current_item = current_item
            if op_state.total_items > 0:
                op_state.progress = current_item / op_state.total_items
        
        if progress is not None:
            op_state.progress = progress
            
        if output_files:
            op_state.output_files.extend(output_files)
        
        self.project_state.last_updated = datetime.now().isoformat()
        self.save_state()
    
    def complete_operation(self, operation_name: str, output_files: List[str] = None):
        """Mark operation as completed"""
        if operation_name not in self.project_state.operations:
            print(f"❌ KRITIK HATA: Bilinmeyen operasyon: {operation_name}")
            sys.exit(1)
        
        op_state = self.project_state.operations[operation_name]
        op_state.status = OperationStatus.COMPLETED
        op_state.progress = 1.0
        op_state.end_time = datetime.now().isoformat()
        
        if output_files:
            op_state.output_files.extend(output_files)
        
        print(f"✅ Operasyon tamamlandı: {operation_name}")
        self.save_state()
    
    def fail_operation(self, operation_name: str, error_message: str):
        """Mark operation as failed"""
        if operation_name not in self.project_state.operations:
            print(f"❌ KRITIK HATA: Bilinmeyen operasyon: {operation_name}")
            sys.exit(1)
        
        op_state = self.project_state.operations[operation_name]
        op_state.status = OperationStatus.FAILED
        op_state.error_message = error_message
        op_state.end_time = datetime.now().isoformat()
        
        print(f"❌ Operasyon başarısız: {operation_name} - {error_message}")
        self.save_state()
        sys.exit(1)  # Maintain sys.exit(1) behavior on errors
    
    def get_operation_state(self, operation_name: str) -> Optional[OperationState]:
        """Get current state of an operation"""
        return self.project_state.operations.get(operation_name)
    
    def is_operation_completed(self, operation_name: str) -> bool:
        """Check if operation is completed"""
        op_state = self.get_operation_state(operation_name)
        return op_state and op_state.status == OperationStatus.COMPLETED
    
    def get_resume_point(self, operation_name: str) -> int:
        """Get the point from which to resume operation"""
        op_state = self.get_operation_state(operation_name)
        if op_state and op_state.status == OperationStatus.IN_PROGRESS:
            return op_state.current_item
        return 0
    
    def save_state(self):
        """Save current state to checkpoint file"""
        try:
            # Convert to serializable format
            data = asdict(self.project_state)
            
            # Convert enums to strings
            data['global_status'] = data['global_status'].value
            for op_name, op_data in data['operations'].items():
                op_data['operation_type'] = op_data['operation_type'].value
                op_data['status'] = op_data['status'].value
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ KRITIK HATA: Checkpoint kaydedilemedi: {e}")
            sys.exit(1)
    
    def cleanup_on_complete_success(self):
        """Clean up temporary files and checkpoint ONLY after complete success"""
        all_completed = all(
            op.status == OperationStatus.COMPLETED 
            for op in self.project_state.operations.values()
        )
        
        if all_completed:
            print("🎉 Tüm operasyonlar başarıyla tamamlandı!")
            
            # Clean up temporary files
            temp_dirs = ['.cache', 'gecici_klipler', 'temp']
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    try:
                        import shutil
                        shutil.rmtree(temp_dir)
                        print(f"🧹 Geçici klasör temizlendi: {temp_dir}")
                    except Exception as e:
                        print(f"⚠️ Geçici klasör temizlenemedi: {temp_dir} - {e}")
            
            # Optionally remove checkpoint file
            try:
                if os.path.exists(self.state_file):
                    os.remove(self.state_file)
                    print(f"🧹 Checkpoint dosyası temizlendi: {self.state_file}")
            except Exception as e:
                print(f"⚠️ Checkpoint dosyası temizlenemedi: {e}")
        else:
            print("⚠️ Bazı operasyonlar henüz tamamlanmadı - geçici dosyalar korunuyor")
    
    def list_output_files(self, operation_name: str = None) -> List[str]:
        """List output files for an operation or all operations"""
        if operation_name:
            op_state = self.get_operation_state(operation_name)
            return op_state.output_files if op_state else []
        else:
            all_files = []
            for op_state in self.project_state.operations.values():
                all_files.extend(op_state.output_files)
            return all_files