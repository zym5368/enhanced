import json
import os
import shutil
import time
from typing import Dict, List, Optional
import torchaudio

class VoiceManager:
    """音色管理器 - 用于保存、加载和管理音色"""
    
    def __init__(self, voices_dir: str = "voices"):
        self.voices_dir = voices_dir
        self.voices_db_path = os.path.join(voices_dir, "voices.json")
        os.makedirs(voices_dir, exist_ok=True)
        self._load_voices_db()
    
    def _load_voices_db(self):
        """加载音色数据库"""
        if os.path.exists(self.voices_db_path):
            try:
                with open(self.voices_db_path, 'r', encoding='utf-8') as f:
                    self.voices_db = json.load(f)
            except:
                self.voices_db = {}
        else:
            self.voices_db = {}
    
    def _save_voices_db(self):
        """保存音色数据库"""
        with open(self.voices_db_path, 'w', encoding='utf-8') as f:
            json.dump(self.voices_db, f, ensure_ascii=False, indent=2)
    
    def save_voice(self, audio_path: str, voice_name: str, description: str = "") -> Dict:
        """保存音色
        
        Args:
            audio_path: 音频文件路径
            voice_name: 音色名称
            description: 音色描述
            
        Returns:
            Dict: 保存结果
        """
        # 检查音色名称是否已存在
        if voice_name in self.voices_db:
            return {"success": False, "message": f"音色名称 '{voice_name}' 已存在"}
        
        # 检查音频文件是否存在
        if not os.path.exists(audio_path):
            return {"success": False, "message": "音频文件不存在"}
        
        # 生成音色ID
        voice_id = f"voice_{int(time.time())}_{len(self.voices_db)}"
        
        # 生成保存路径
        file_extension = os.path.splitext(audio_path)[1]
        saved_audio_path = os.path.join(self.voices_dir, f"{voice_id}{file_extension}")
        
        try:
            # 复制音频文件
            shutil.copy2(audio_path, saved_audio_path)
            
            # 验证音频文件
            try:
                audio_info = torchaudio.info(saved_audio_path)
                duration = audio_info.num_frames / audio_info.sample_rate
            except:
                duration = 0
            
            # 保存到数据库
            voice_info = {
                "id": voice_id,
                "name": voice_name,
                "description": description,
                "audio_path": saved_audio_path,
                "created_time": time.time(),
                "duration": duration,
                "sample_rate": audio_info.sample_rate if 'audio_info' in locals() else 0,
                "file_size": os.path.getsize(saved_audio_path)
            }
            
            self.voices_db[voice_name] = voice_info
            self._save_voices_db()
            
            return {
                "success": True, 
                "message": f"音色 '{voice_name}' 保存成功",
                "voice_info": voice_info
            }
            
        except Exception as e:
            # 清理失败的文件
            if os.path.exists(saved_audio_path):
                os.remove(saved_audio_path)
            return {"success": False, "message": f"保存失败: {str(e)}"}
    
    def get_voice(self, voice_name: str) -> Optional[Dict]:
        """获取音色信息
        
        Args:
            voice_name: 音色名称
            
        Returns:
            Optional[Dict]: 音色信息，如果不存在返回None
        """
        return self.voices_db.get(voice_name)
    
    def get_voice_audio_path(self, voice_name: str) -> Optional[str]:
        """获取音色音频路径
        
        Args:
            voice_name: 音色名称
            
        Returns:
            Optional[str]: 音频文件路径，如果不存在返回None
        """
        voice_info = self.get_voice(voice_name)
        if voice_info and os.path.exists(voice_info["audio_path"]):
            return voice_info["audio_path"]
        return None
    
    def list_voices(self) -> List[Dict]:
        """获取所有音色列表
        
        Returns:
            List[Dict]: 音色列表
        """
        voices = []
        for voice_name, voice_info in self.voices_db.items():
            # 检查音频文件是否还存在
            if os.path.exists(voice_info["audio_path"]):
                voices.append({
                    "name": voice_name,
                    "description": voice_info.get("description", ""),
                    "duration": voice_info.get("duration", 0),
                    "created_time": voice_info.get("created_time", 0),
                    "file_size": voice_info.get("file_size", 0)
                })
        
        # 按创建时间排序
        voices.sort(key=lambda x: x["created_time"], reverse=True)
        return voices
    
    def delete_voice(self, voice_name: str) -> Dict:
        """删除音色
        
        Args:
            voice_name: 音色名称
            
        Returns:
            Dict: 删除结果
        """
        if voice_name not in self.voices_db:
            return {"success": False, "message": f"音色 '{voice_name}' 不存在"}
        
        voice_info = self.voices_db[voice_name]
        
        try:
            # 删除音频文件
            if os.path.exists(voice_info["audio_path"]):
                os.remove(voice_info["audio_path"])
            
            # 从数据库删除
            del self.voices_db[voice_name]
            self._save_voices_db()
            
            return {
                "success": True,
                "message": f"音色 '{voice_name}' 删除成功"
            }
            
        except Exception as e:
            return {"success": False, "message": f"删除失败: {str(e)}"}
    
    def search_voices(self, keyword: str) -> List[Dict]:
        """搜索音色
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            List[Dict]: 匹配的音色列表
        """
        all_voices = self.list_voices()
        if not keyword:
            return all_voices
        
        keyword = keyword.lower()
        matched_voices = []
        
        for voice in all_voices:
            if (keyword in voice["name"].lower() or 
                keyword in voice.get("description", "").lower()):
                matched_voices.append(voice)
        
        return matched_voices 