"""Unit tests for the dithertone rendering engine."""

import numpy as np
import pytest

from webcam_dither.core.dithertone import DithertoneRenderer, DithertoneParams


class TestDithertoneParams:
    """Test parameter clamping and defaults."""

    def test_defaults(self):
        p = DithertoneParams()
        assert p.spacing == 8
        assert p.gamma == 1.0
        assert p.contrast == 0.0
        assert p.brightness == 0.0
        assert p.invert is False

    def test_clamp_spacing_min(self):
        p = DithertoneParams(spacing=1)
        p.clamp()
        assert p.spacing == 3

    def test_clamp_spacing_max(self):
        p = DithertoneParams(spacing=100)
        p.clamp()
        assert p.spacing == 40

    def test_clamp_gamma(self):
        p = DithertoneParams(gamma=0.01)
        p.clamp()
        assert p.gamma == 0.2
        p.gamma = 10.0
        p.clamp()
        assert p.gamma == 5.0

    def test_clamp_contrast(self):
        p = DithertoneParams(contrast=-200)
        p.clamp()
        assert p.contrast == -100.0


class TestDithertoneRenderer:
    """Test the rendering engine."""

    def test_render_returns_correct_shape(self):
        renderer = DithertoneRenderer()
        gray = np.full((100, 120), 128, dtype=np.uint8)
        result = renderer.render(gray)
        assert result.shape == (100, 120)
        assert result.dtype == np.uint8

    def test_render_white_input_no_dots(self):
        """A fully white image should produce no dots (all white output)."""
        renderer = DithertoneRenderer(DithertoneParams(spacing=10))
        white = np.full((100, 100), 255, dtype=np.uint8)
        result = renderer.render(white)
        # Output should be entirely white (255)
        assert np.all(result == 255)

    def test_render_black_input_has_dots(self):
        """A fully black image should produce maximum dots."""
        renderer = DithertoneRenderer(DithertoneParams(spacing=10))
        black = np.zeros((100, 100), dtype=np.uint8)
        result = renderer.render(black)
        # Output should have black pixels (dots) on white background
        assert np.any(result == 0), "Black input should produce dots"
        assert np.any(result == 255), "Should still have white background between dots"

    def test_render_inverted(self):
        """Inverted mode: white dots on black background."""
        renderer = DithertoneRenderer(DithertoneParams(spacing=10, invert=True))
        black = np.zeros((100, 100), dtype=np.uint8)
        result = renderer.render(black)
        # Inverted + black input = no dots, all black background
        assert np.all(result == 0)

    def test_render_inverted_white_input(self):
        """Inverted mode with white input should produce white dots."""
        renderer = DithertoneRenderer(DithertoneParams(spacing=10, invert=True))
        white = np.full((100, 100), 255, dtype=np.uint8)
        result = renderer.render(white)
        # Should have white dots on black background
        assert np.any(result == 255), "White input in invert mode should produce dots"
        assert np.any(result == 0), "Should still have black background"

    def test_darker_produces_larger_dots(self):
        """Darker regions should have more black pixels than lighter ones."""
        params = DithertoneParams(spacing=6)
        renderer = DithertoneRenderer(params)

        dark = np.full((60, 60), 30, dtype=np.uint8)
        light = np.full((60, 60), 200, dtype=np.uint8)

        dark_result = renderer.render(dark)
        light_result = renderer.render(light)

        dark_black_count = np.sum(dark_result < 128)
        light_black_count = np.sum(light_result < 128)

        assert dark_black_count > light_black_count, (
            f"Dark input should produce more black pixels ({dark_black_count}) "
            f"than light input ({light_black_count})"
        )

    def test_adjust_spacing(self):
        renderer = DithertoneRenderer()
        original = renderer.params.spacing
        renderer.adjust_spacing(2)
        assert renderer.params.spacing == original + 2
        renderer.adjust_spacing(-5)
        assert renderer.params.spacing == original - 3

    def test_adjust_gamma(self):
        renderer = DithertoneRenderer()
        renderer.adjust_gamma(0.5)
        assert renderer.params.gamma == 1.5

    def test_toggle_invert(self):
        renderer = DithertoneRenderer()
        assert renderer.params.invert is False
        renderer.toggle_invert()
        assert renderer.params.invert is True
        renderer.toggle_invert()
        assert renderer.params.invert is False

    def test_reset(self):
        renderer = DithertoneRenderer()
        renderer.adjust_spacing(10)
        renderer.adjust_gamma(1.0)
        renderer.toggle_invert()
        renderer.reset()
        assert renderer.params.spacing == 8
        assert renderer.params.gamma == 1.0
        assert renderer.params.invert is False

    def test_get_status_text(self):
        renderer = DithertoneRenderer()
        text = renderer.get_status_text()
        assert "Spacing:8" in text
        assert "Gamma:1.0" in text
        assert "Invert:OFF" in text

    def test_clone_with_spacing(self):
        renderer = DithertoneRenderer(DithertoneParams(
            spacing=10, gamma=2.0, contrast=20, invert=True
        ))
        clone = renderer.clone_with_spacing(5)
        assert clone.params.spacing == 5
        assert clone.params.gamma == 2.0
        assert clone.params.contrast == 20
        assert clone.params.invert is True

    def test_brightness_adjustment(self):
        """Increasing brightness should reduce dot coverage."""
        params_normal = DithertoneParams(spacing=8, brightness=0)
        params_bright = DithertoneParams(spacing=8, brightness=80)

        gray = np.full((80, 80), 128, dtype=np.uint8)

        result_normal = DithertoneRenderer(params_normal).render(gray)
        result_bright = DithertoneRenderer(params_bright).render(gray)

        normal_dots = np.sum(result_normal < 128)
        bright_dots = np.sum(result_bright < 128)

        assert bright_dots < normal_dots, (
            "Higher brightness should produce fewer dots"
        )

    def test_gamma_effect(self):
        """Higher gamma should lighten midtones, reducing dot count."""
        gray = np.full((80, 80), 128, dtype=np.uint8)

        result_low = DithertoneRenderer(DithertoneParams(gamma=0.5)).render(gray)
        result_high = DithertoneRenderer(DithertoneParams(gamma=2.0)).render(gray)

        low_dots = np.sum(result_low < 128)
        high_dots = np.sum(result_high < 128)

        assert low_dots > high_dots, (
            "Lower gamma should produce more dots (darker midtones)"
        )
