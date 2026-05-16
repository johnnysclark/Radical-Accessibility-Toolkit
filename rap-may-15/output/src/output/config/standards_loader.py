"""
Configuration loader for tactile standards.

Loads and parses the tactile_standards.yaml configuration file.
"""

import yaml
from pathlib import Path
from typing import Optional, Dict, Any


class StandardsLoaderError(Exception):
    """Custom exception for configuration loading errors."""
    pass


class StandardsLoader:
    """
    Loader for tactile standards YAML configuration.

    Provides access to processing defaults, paper sizes, density limits,
    and other configuration settings.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize standards loader.

        Args:
            config_path: Optional path to custom tactile_standards.yaml file.
                        If not provided, uses default bundled configuration.
        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Default to bundled configuration
            package_dir = Path(__file__).parent.parent
            self.config_path = package_dir / "data" / "tactile_standards.yaml"

        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Returns:
            Configuration dictionary

        Raises:
            StandardsLoaderError: If configuration cannot be loaded
        """
        if not self.config_path.exists():
            raise StandardsLoaderError(
                f"Configuration file not found: {self.config_path}"
            )

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            if not config:
                raise StandardsLoaderError("Configuration file is empty")

            return config

        except yaml.YAMLError as e:
            raise StandardsLoaderError(
                f"Failed to parse YAML configuration: {str(e)}"
            ) from e
        except Exception as e:
            raise StandardsLoaderError(
                f"Failed to load configuration: {str(e)}"
            ) from e

    def get_default_threshold(self) -> int:
        """
        Get default threshold value for B&W conversion.

        Returns:
            Default threshold (0-255)
        """
        return self.config.get('processing', {}).get('default_threshold', 128)

    def get_output_dpi(self) -> int:
        """
        Get target output DPI.

        Returns:
            DPI value
        """
        return self.config.get('processing', {}).get('output_dpi', 300)

    def get_paper_size(self, size_name: str) -> Dict[str, float]:
        """
        Get paper size dimensions.

        Args:
            size_name: Paper size name (e.g., 'letter', 'tabloid')

        Returns:
            Dictionary with 'width' and 'height' in inches

        Raises:
            StandardsLoaderError: If paper size not found
        """
        paper_sizes = self.config.get('paper_sizes', {})

        if size_name not in paper_sizes:
            available = ', '.join(paper_sizes.keys())
            raise StandardsLoaderError(
                f"Paper size '{size_name}' not found. "
                f"Available sizes: {available}"
            )

        return paper_sizes[size_name]

    def get_density_limits(self) -> Dict[str, float]:
        """
        Get density management settings.

        Returns:
            Dictionary with density thresholds
        """
        return self.config.get('density', {
            'max_black_percentage': 45,
            'warning_threshold': 40,
            'target_optimal': 30
        })

    def get_max_density(self) -> float:
        """
        Get maximum acceptable black pixel density.

        Returns:
            Maximum density percentage
        """
        return self.get_density_limits().get('max_black_percentage', 45)

    def get_warning_threshold(self) -> float:
        """
        Get density warning threshold.

        Returns:
            Warning threshold percentage
        """
        return self.get_density_limits().get('warning_threshold', 40)

    def get_target_density(self) -> float:
        """
        Get target optimal density.

        Returns:
            Target density percentage
        """
        return self.get_density_limits().get('target_optimal', 30)

    def get_supported_formats(self) -> list:
        """
        Get list of supported file formats.

        Returns:
            List of file extensions (e.g., ['.jpg', '.png'])
        """
        return self.config.get('supported_formats', [
            '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif', '.pdf'
        ])

    def get_line_standards(self) -> Dict[str, float]:
        """
        Get line thickness standards.

        Returns:
            Dictionary with line thickness values in pixels at 300 DPI
        """
        return self.config.get('line_standards', {
            'minimum_thickness': 1.5,
            'wall_thickness': 3,
            'detail_thickness': 2
        })

    def get_all_config(self) -> Dict[str, Any]:
        """
        Get complete configuration dictionary.

        Returns:
            Full configuration
        """
        return self.config

    def reload(self):
        """
        Reload configuration from file.

        Useful if configuration file has been modified.
        """
        self.config = self._load_config()
