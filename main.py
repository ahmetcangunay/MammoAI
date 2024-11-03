import os
import sys
sys.path.append('./src/models')
from typing import Optional
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPalette, QColor
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFileDialog,
                             QCheckBox, QGroupBox, QMessageBox, QScrollArea)
import pydicom
from report_creator import ReportCreator
from birads_classifier import BiradsClassifier
from density_classifier import DensityClassifier
from mass_calcification_classifier import MassCalcificationClassfier
from quadrant_analyzer import QuadrantAnalyzer
from symmetry_classifier import SymmetryClassifier


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DICOM Analysis Application")
        self.setGeometry(100, 100, 1200, 800)
        self.image = 5

        # Apply dark theme
        self.apply_dark_theme()

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Left side - Image display
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Create scroll area for image
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumWidth(600)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: 1px solid #333333;
            }
            QScrollBar:vertical {
                background-color: #1e1e1e;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #424242;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Image label inside scroll area
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #1e1e1e;")
        scroll_area.setWidget(self.image_label)

        left_layout.addWidget(scroll_area)
        main_layout.addWidget(left_widget)

        # Right side - Controls
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Upload button
        self.upload_button = QPushButton("Upload DICOM Image")
        self.upload_button.setMinimumHeight(40)
        self.upload_button.clicked.connect(self.load_dicom)
        right_layout.addWidget(self.upload_button)

        # Checkbox group
        checkbox_group = QGroupBox("Analysis Options")
        checkbox_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #424242;
                border-radius: 5px;
                margin-top: 1ex;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
        """)
        checkbox_layout = QVBoxLayout()

        self.checkboxes = {
            'birads': QCheckBox("BIRADS Classification"),
            'density': QCheckBox("Density Classification"),
            'mass_calc': QCheckBox("Mass and Calcification Classification"),
            'quadrant': QCheckBox("Quadrant Analysis"),
            'symmetry': QCheckBox("Symmetry Analysis")
        }

        for checkbox in self.checkboxes.values():
            checkbox.setStyleSheet("""
                QCheckBox {
                    spacing: 10px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
                QCheckBox::indicator:unchecked {
                    border: 2px solid #424242;
                    background-color: #1e1e1e;
                }
                QCheckBox::indicator:checked {
                    border: 2px solid #0078d4;
                    background-color: #0078d4;
                }
            """)
            checkbox_layout.addWidget(checkbox)

        checkbox_group.setLayout(checkbox_layout)
        right_layout.addWidget(checkbox_group)

        # Run and Report buttons
        self.run_button = QPushButton("Run Analysis")
        self.run_button.setMinimumHeight(40)
        self.run_button.clicked.connect(self.run_analysis)
        self.run_button.setEnabled(False)

        self.report_button = QPushButton("Generate Report")
        self.report_button.setMinimumHeight(40)
        self.report_button.clicked.connect(self.generate_report)
        self.report_button.setEnabled(False)

        right_layout.addWidget(self.run_button)
        right_layout.addWidget(self.report_button)

        # Add stretch to push buttons to top
        right_layout.addStretch()

        # Add right widget to main layout
        main_layout.addWidget(right_widget)

        # Initialize variables
        self.dicom_data = None
        self.image_data = None
        self.analysis_results = {}

    def apply_dark_theme(self):
        # Set dark theme palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(15, 15, 15))
        dark_palette.setColor(QPalette.AlternateBase, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(0, 120, 212))
        dark_palette.setColor(QPalette.Highlight, QColor(0, 120, 212))
        dark_palette.setColor(QPalette.HighlightedText, Qt.white)

        self.setPalette(dark_palette)

        # Set stylesheet for the main window
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QPushButton {
                background-color: #0078d4;
                border: none;
                border-radius: 5px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #006cbd;
            }
            QPushButton:disabled {
                background-color: #424242;
                color: #888888;
            }
        """)

    def load_dicom(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select DICOM file", "", "DICOM Files (*.dcm)")

        if file_name:
            try:
                # Load DICOM file
                self.dicom_data = pydicom.dcmread(file_name)

                # Convert DICOM to QImage
                image_array = self.dicom_data.pixel_array
                height, width = image_array.shape

                # Normalize to 8-bit for display
                image_8bit = ((image_array - image_array.min()) /
                              (image_array.max() - image_array.min()) * 255).astype('uint8')

                q_img = QImage(image_8bit.data, width, height, width,
                               QImage.Format_Grayscale8)
                pixmap = QPixmap.fromImage(q_img)

                # Scale if necessary while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(self.image_label.size(),
                                              Qt.KeepAspectRatio,
                                              Qt.SmoothTransformation)

                self.image_label.setPixmap(scaled_pixmap)
                self.image_data = image_array

                # Enable run button
                self.run_button.setEnabled(True)

                # Show success message
                QMessageBox.information(
                    self, "Success", "DICOM image loaded successfully")

            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Error loading DICOM file: {str(e)}")

    def run_analysis(self):
        if not self.image_data is not None:
            QMessageBox.warning(
                self, "Warning", "Please load a DICOM image first")
            return

        try:
            # Clear previous results
            self.analysis_results = {}

            # Run selected analyses
            if self.checkboxes['birads'].isChecked():
                self.analysis_results['birads'] = BiradsClassifier.get_birads_type(self,
                                                                                   image=self.image)

            if self.checkboxes['density'].isChecked():
                self.analysis_results['density'] = DensityClassifier.get_density_type(self,
                                                                                      image=self.image)

            if self.checkboxes['mass_calc'].isChecked():
                self.analysis_results['mass_calc'] = MassCalcificationClassfier.get_mass_calcification_type(self,
                                                                                                            image=self.image)

            if self.checkboxes['quadrant'].isChecked():
                self.analysis_results['quadrant'] = QuadrantAnalyzer.get_quadrants(self, image=self.image
                                                                                   )

            if self.checkboxes['symmetry'].isChecked():
                self.analysis_results['symmetry'] = SymmetryClassifier.get_symmetry_type(self, image=self.image
                                                                                         )

            # Enable report button if we have results
            if self.analysis_results:
                self.report_button.setEnabled(True)
                QMessageBox.information(
                    self, "Success", "Analysis completed successfully")
            else:
                QMessageBox.warning(
                    self, "Warning", "Please select at least one analysis option")

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Error during analysis: {str(e)}")

    def generate_report(self):
        try:
            # Create ReportCreator instance with analysis results
            report_creator = ReportCreator(self.analysis_results)

            # Get selected analysis types
            selected_analyses = [
                key for key, checkbox in self.checkboxes.items() if checkbox.isChecked()]

            # Generate report with only selected analyses
            report = report_creator.generate_report(
                self.image_data, selected_analyses)

            # Ask for save location
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save Report", "", "Text Files (*.txt)")

            if file_name:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(report)
                QMessageBox.information(
                    self, "Success", f"Report saved successfully to {file_name}")

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Error generating report: {str(e)}")


def main():
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
