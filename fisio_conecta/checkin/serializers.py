from rest_framework import serializers
from fisio_conecta import models as m


class CheckInOutSerializer(serializers.ModelSerializer):
    class meta:
        model = m.CheckInOut
        fields = '__all__'

class CheckInOutAggregateSerializer:
    """
    Serializa uma lista de registros de CheckInOut em formato unificado,
    alternando os valores de check-in e check-out em uma única estrutura.

    Exemplo de retorno:
    {
        "checkin": {
            "nivel_dor": [8, 7, 6, 5],
            "bem_estar": [4, 5, 6, 7],
            "confianca": [7, 8, 8, 9],
            "mudanca": [5, 6, 6, 7]
        }
    }
    """

    FIELDS_MAP = {
        "nivel_dor": "pergunta_dor",
        "bem_estar": "pergunta_bem_estar",
        "confianca": "pergunta_confianca",
        "mudanca": "pergunta_mudanca",
    }

    def to_representation(self, instances, reverse=False):
        if not instances:
            return {"checkin": {}}

        items = list(instances[::-1]) if reverse else list(instances)

        result = {"checkin": {key: [] for key in self.FIELDS_MAP}}

        for item in items:
            for label, attr in self.FIELDS_MAP.items():
                result["checkin"][label].append(getattr(item, attr, None))

        return result

