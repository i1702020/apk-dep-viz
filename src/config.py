"""Configuration model and validation."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Config:
    """User-configurable parameters of the application."""

    package: str
    repo: str
    test_mode: bool = False
    max_depth: int = 10
    filter_substr: Optional[str] = None

    def validate(self) -> None:
        """Validate all configuration parameters. Raises ValueError on error."""
        if not self.package or not self.package.strip():
            raise ValueError("Имя пакета не может быть пустым (--package)")

        if not self.repo or not self.repo.strip():
            raise ValueError("URL/путь репозитория не может быть пустым (--repo)")

        if self.max_depth < 0:
            raise ValueError("Максимальная глубина должна быть >= 0 (--depth)")

        if self.max_depth > 100:
            raise ValueError("Максимальная глубина слишком большая (>100)")

        if self.test_mode:
            path = Path(self.repo)
            if not path.exists():
                raise ValueError(f"Файл тестового репозитория не найден: {self.repo}")
            if not path.is_file():
                raise ValueError(f"Путь тестового репозитория не является файлом: {self.repo}")

    def as_dict(self) -> dict:
        """Return parameters as key-value dictionary for Stage 1 output."""
        return {
            "package": self.package,
            "repo": self.repo,
            "test_mode": self.test_mode,
            "max_depth": self.max_depth,
            "filter_substr": self.filter_substr or "",
        }
