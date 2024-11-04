import time
from typing import Dict, List, Any


class ReportCreator:
    def __init__(self, analysis_results: Dict[str, Any]):
        """
        Initialize ReportCreator with analysis results.

        Args:
            analysis_results (Dict[str, Any]): Dictionary containing results of various analyses
        """
        self.analysis_results = analysis_results

    def generate_report(self, image_data: Any, selected_analyses: List[str]) -> str:
        """
        Generate a report based on selected analyses.

        Args:
            image_data: The image data used in analysis
            selected_analyses (List[str]): List of analysis types to include in report

        Returns:
            str: Formatted report text
        """
        # Get current date
        current_date = time.strftime("%d-%m-%Y, %H:%M:%S")

        # Start with report header
        report = f"""MAMOGRAFİ RAPORU
-------------------
Tarih: {current_date}

BULGULAR:\n"""

        # Add selected analysis results to report
        for analysis_type in selected_analyses:
            if analysis_type in self.analysis_results:
                result = self.analysis_results[analysis_type]

                if analysis_type == 'birads':
                    report += f"- BIRADS Sınıflandırması: {result[0]}\n- Risk Değerlendirmesi: {result[1]}\n"

                elif analysis_type == 'density':
                    report += f"- Meme Yoğunluğu: {result}\n"

                elif analysis_type == 'mass_calc':
                    mass_status = "Malign" if result['mass_type'] == "MALIGNANT" else "Benign"
                    calc_status = "Malign" if result['calcification_type'] == "MALIGNANT" else "Normal"
                    report += f"- Kitle Değerlendirmesi: {mass_status}\n"
                    report += f"- Kalsifikasyon Değerlendirmesi: {calc_status}\n"

                elif analysis_type == 'quadrant':
                    report += f"- Kadran Analizi: {result}\n"

                elif analysis_type == 'symmetry':
                    symmetry_text = "Asimetrik" if result == "ASYMMETRIC" else "Simetrik"
                    report += f"- Simetri Değerlendirmesi: {symmetry_text} meme yapısı\n"

        return report
