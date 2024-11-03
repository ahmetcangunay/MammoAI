class BiradsClassifier:

    # TODO: Add Birads Classifier model
    def __init__(self, data) -> None:
        self.data = data

    def get_birads_type(self, image) -> str:
        birads_type = 'BIRADS 5'  # TODO: Implement the logic

        risk_mapping = {
            'BIRADS 1': 'Düşük Risk',
            'BIRADS 2': 'Düşük Risk',
            'BIRADS 3': 'Orta Risk',
            'BIRADS 4': 'Yüksek Risk',
            'BIRADS 5': 'Çok Yüksek Risk'
        }
        return birads_type, risk_mapping.get(birads_type, 'Belirsiz Risk')
