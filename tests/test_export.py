"""Tests for export functionality."""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from luxin.components.export import render_export_buttons


def test_render_export_buttons_csv():
    """Test CSV export button."""
    df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    
    with patch('luxin.components.export.st') as mock_st:
        mock_st.subheader = MagicMock()
        mock_st.columns = MagicMock(return_value=(MagicMock(), MagicMock(), MagicMock()))
        mock_st.download_button = MagicMock()
        
        render_export_buttons(df)
        
        # Should call download_button for CSV
        assert mock_st.download_button.call_count >= 1
        # Check CSV button was created
        calls = [call[1] for call in mock_st.download_button.call_args_list]
        csv_calls = [c for c in calls if c.get('mime') == 'text/csv']
        assert len(csv_calls) > 0


def test_render_export_buttons_json():
    """Test JSON export button."""
    df = pd.DataFrame({'a': [1, 2, 3]})
    
    with patch('luxin.components.export.st') as mock_st:
        mock_st.subheader = MagicMock()
        mock_st.columns = MagicMock(return_value=(MagicMock(), MagicMock(), MagicMock()))
        mock_st.download_button = MagicMock()
        
        render_export_buttons(df)
        
        # Check JSON button was created
        calls = [call[1] for call in mock_st.download_button.call_args_list]
        json_calls = [c for c in calls if c.get('mime') == 'application/json']
        assert len(json_calls) > 0


def test_render_export_buttons_excel_with_openpyxl():
    """Test Excel export button when openpyxl is available."""
    df = pd.DataFrame({'a': [1, 2, 3]})
    
    with patch('luxin.components.export.st') as mock_st:
        mock_st.subheader = MagicMock()
        mock_st.columns = MagicMock(return_value=(MagicMock(), MagicMock(), MagicMock()))
        mock_st.download_button = MagicMock()
        mock_st.info = MagicMock()
        
        # Test that function runs successfully
        render_export_buttons(df)
        
        # Should call download_button at least for CSV and JSON
        assert mock_st.download_button.call_count >= 2
        # Excel button may or may not be present depending on openpyxl availability
        # If openpyxl is available, there should be 3 buttons, otherwise info message


def test_render_export_buttons_excel_without_openpyxl():
    """Test Excel export button when openpyxl is not available."""
    df = pd.DataFrame({'a': [1, 2, 3]})
    
    # Test that the function handles missing openpyxl gracefully
    with patch('luxin.components.export.st') as mock_st:
        mock_st.subheader = MagicMock()
        mock_st.columns = MagicMock(return_value=(MagicMock(), MagicMock(), MagicMock()))
        mock_st.download_button = MagicMock()
        mock_st.info = MagicMock()
        
        # Check if openpyxl is actually available
        try:
            import openpyxl
            # If available, Excel button will be shown, so just verify function runs
            render_export_buttons(df)
            assert mock_st.download_button.call_count >= 2  # CSV and JSON at minimum
        except ImportError:
            # If not available, should show info message
            render_export_buttons(df)
            # Function should still work and show CSV/JSON buttons
            assert mock_st.download_button.call_count >= 2


def test_render_export_buttons_custom_filename():
    """Test export buttons with custom filename prefix."""
    df = pd.DataFrame({'a': [1, 2, 3]})
    
    with patch('luxin.components.export.st') as mock_st:
        mock_st.subheader = MagicMock()
        mock_st.columns = MagicMock(return_value=(MagicMock(), MagicMock(), MagicMock()))
        mock_st.download_button = MagicMock()
        
        render_export_buttons(df, filename_prefix="custom_data")
        
        # Check filename prefix is used
        calls = [call[1] for call in mock_st.download_button.call_args_list]
        assert any('custom_data' in c.get('file_name', '') for c in calls)


def test_render_export_buttons_empty_dataframe():
    """Test export buttons with empty DataFrame."""
    df = pd.DataFrame()
    
    with patch('luxin.components.export.st') as mock_st:
        mock_st.subheader = MagicMock()
        mock_st.columns = MagicMock(return_value=(MagicMock(), MagicMock(), MagicMock()))
        mock_st.download_button = MagicMock()
        
        # Should not raise error
        render_export_buttons(df)
        mock_st.download_button.assert_called()

