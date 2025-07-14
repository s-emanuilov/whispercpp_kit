import logging
import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path
import hashlib
import ffmpeg
from typing import Optional, Union
from dataclasses import dataclass


class WhisperCPPError(Exception):
    """Base exception for WhisperCPP errors"""

    pass


@dataclass
class WhisperState:
    is_repo_ready: bool = False
    is_built: bool = False
    is_model_ready: bool = False


class WhisperCPP:
    SAMPLE_RATE = 16000
    DEFAULT_CACHE_DIR = Path(tempfile.gettempdir()) / "whisper-cpp-cache"
    DEFAULT_LIB_DIR = Path.home() / ".whisper.cpp"
    DEFAULT_THREADS = os.cpu_count() or 1

    def __init__(
        self,
        model_path: Optional[Union[str, Path]] = None,
        model_name: str = "base.en",
        lib_dir: Optional[Union[str, Path]] = None,
        cache_dir: Optional[Union[str, Path]] = None,
        log_level: int = logging.INFO,
        skip_checks: bool = False,
        num_threads: Optional[int] = None,
        verbose: bool = False,
    ):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            self.logger.addHandler(handler)

        self.base_path = Path(lib_dir) if lib_dir else self.DEFAULT_LIB_DIR
        self.cache_dir = Path(cache_dir) if cache_dir else self.DEFAULT_CACHE_DIR
        self.model_path = Path(model_path) if model_path else None
        self.model_name = model_name
        self.state = WhisperState()

        self.system = platform.system().lower()
        self._setup_platform_configs()

        self.num_threads = num_threads if num_threads is not None else self.DEFAULT_THREADS
        
        if self.num_threads < 1:
            raise WhisperCPPError("Number of threads must be at least 1")

        self.verbose = verbose
        
        if not skip_checks:
            self._check_requirements()
            self.setup()

    def _setup_platform_configs(self) -> None:
        self.platform_configs = {
            "linux": {
                "binary_name": "whisper-cli",
                "cmake_args": ["-DCMAKE_BUILD_TYPE=Release"],
            },
            "darwin": {
                "binary_name": "whisper-cli",
                "cmake_args": ["-DCMAKE_BUILD_TYPE=Release"],
            },
        }

        if self.system not in self.platform_configs:
            raise WhisperCPPError(f"Unsupported platform: {self.system}")

        self.platform_config = self.platform_configs[self.system]

    def _is_binary_ready(self) -> bool:
        """Check if the whisper binary is ready"""
        binary_path = (
            self.base_path / "build" / "bin" / self.platform_config["binary_name"]
        )
        return binary_path.exists() and binary_path.is_file()

    def _is_repo_valid(self) -> bool:
        """Check if the repository is valid"""
        git_dir = self.base_path / ".git"
        whisper_cpp = self.base_path / "CMakeLists.txt"
        return git_dir.exists() and whisper_cpp.exists()

    def _is_model_valid(self) -> bool:
        """Check if the model file is valid"""
        if self.model_path is None:
            self.model_path = self.base_path / "models" / f"ggml-{self.model_name}.bin"
        return self.model_path.exists() and self.model_path.stat().st_size > 0

    def check_ready(self) -> bool:
        """Check if everything is ready for transcription"""
        if not all(
            [self.state.is_repo_ready, self.state.is_built, self.state.is_model_ready]
        ):
            self.state.is_repo_ready = self._is_repo_valid()
            self.state.is_built = self._is_binary_ready()
            self.state.is_model_ready = self._is_model_valid()

        return all(
            [self.state.is_repo_ready, self.state.is_built, self.state.is_model_ready]
        )

    def _check_requirements(self) -> None:
        """Check if all required system commands are available"""
        required_commands = ["git", "cmake", "ffmpeg", "make", "g++", "gcc"]
        missing = [cmd for cmd in required_commands if not shutil.which(cmd)]
        if missing:
            missing_str = " ".join(missing)
            raise WhisperCPPError(
                f"Missing required commands: {', '.join(missing)}. "
                "Please install them using your system's package manager:\n"
                f"- For Ubuntu/Debian: sudo apt-get install {missing_str} build-essential\n"
                f"- For CentOS/RHEL: sudo yum install {missing_str} gcc-c++ make\n"
                f"- For macOS: brew install {missing_str}"
            )

    def setup(self) -> None:
        """Setup whisper.cpp library and model only if needed"""
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
            self.cache_dir.mkdir(parents=True, exist_ok=True)

            if not self.check_ready():
                if not self.state.is_repo_ready:
                    self._setup_repository()
                if not self.state.is_model_ready:
                    self._setup_model()
                if not self.state.is_built:
                    self._build_library()

                # Final verification
                if not self.check_ready():
                    raise WhisperCPPError("Setup failed: System not ready after setup")
            else:
                self.logger.info("System already set up and ready")

        except subprocess.CalledProcessError as e:
            raise WhisperCPPError(
                f"Setup failed: {e.stderr.decode() if e.stderr else str(e)}"
            )

    def _setup_repository(self) -> None:
        if not self._is_repo_valid():
            self.logger.info("Setting up whisper.cpp repository...")
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--recurse-submodules",
                    "https://github.com/ggerganov/whisper.cpp.git",
                    str(self.base_path),
                ],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                [
                    "git",
                    "checkout",
                    "v1.7.6",
                ],
                cwd=self.base_path,
                check=True,
                capture_output=True,
            )
            # Ensure submodules are up to date after checkout
            subprocess.run(
                ["git", "submodule", "update", "--init", "--recursive"],
                cwd=self.base_path,
                check=True,
                capture_output=True,
            )
        self.state.is_repo_ready = True

    def _setup_model(self) -> None:
        if not self._is_model_valid():
            self.logger.info(f"Setting up model: {self.model_name}")
            model_script = self.base_path / "models" / "download-ggml-model.sh"
            subprocess.run(
                ["bash", str(model_script), self.model_name],
                cwd=self.base_path,
                check=True,
                capture_output=True,
            )
        self.state.is_model_ready = True

    def _build_library(self) -> None:
        if not self._is_binary_ready():
            self.logger.info("Building whisper.cpp...")
            build_path = self.base_path / "build"
            build_path.mkdir(exist_ok=True)

            subprocess.run(
                ["cmake", "-B", str(build_path)] + self.platform_config["cmake_args"],
                cwd=self.base_path,
                check=True,
                capture_output=True,
            )

            subprocess.run(
                [
                    "cmake",
                    "--build",
                    str(build_path),
                    "--config",
                    "Release",
                    "-j",
                    str(os.cpu_count() or 1),
                ],
                check=True,
                capture_output=True,
            )
        self.state.is_built = True

    def transcribe(
        self,
        audio_path: Union[str, Path],
        convert: bool = True,
        language: Optional[str] = None,
        translate: bool = False,
        prompt: Optional[str] = None,
    ) -> str:
        """Transcribe audio file"""
        if not self.check_ready():
            raise WhisperCPPError("System not ready. Run setup() first")

        if convert:
            audio_path = self.convert_audio(audio_path)

        cmd = [
            str(self.base_path / "build" / "bin" / self.platform_config["binary_name"]),
            "-m",
            str(self.model_path),
            "-f",
            str(audio_path),
            "-nt",
            "-t",
            str(self.num_threads),
        ]
        
        if self.verbose:
            cmd.append("-debug")
            
        if language:
            cmd.extend(["-l", language])
        if translate:
            cmd.append("--translate")
        if prompt:
            cmd.extend(["--prompt", prompt])

        try:
            result = subprocess.run(
                cmd, 
                capture_output=not self.verbose,
                text=True, 
                check=True
            )
            return result.stdout.strip() if not self.verbose else "Output printed to console"
        except subprocess.CalledProcessError as e:
            raise WhisperCPPError(f"Transcription failed: {e.stderr}")

    def convert_audio(self, audio_path: Union[str, Path]) -> str:
        """Convert audio with caching"""
        input_path = Path(audio_path)
        cache_key = hashlib.md5(str(input_path.absolute()).encode()).hexdigest()
        cache_path = self.cache_dir / f"{cache_key}.wav"

        if cache_path.exists():
            self.logger.debug("Using cached converted audio")
            return str(cache_path)

        try:
            self.logger.debug("Converting audio...")
            stream = ffmpeg.input(str(input_path))
            stream = ffmpeg.output(
                stream, str(cache_path), ar=self.SAMPLE_RATE, ac=1, acodec="pcm_s16le"
            )
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            return str(cache_path)
        except ffmpeg.Error as e:
            raise WhisperCPPError(f"Audio conversion failed: {e.stderr.decode()}")