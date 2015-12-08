import requests

from cloudbot import hook
from cloudbot.util import formatting

import json

api_url = 'http://developers.agenciaideias.com.br/loterias/megasena/json'


@hook.command("megasena", autohelp=False)
def megasena(text):

    r = requests.get(api_url).json()
    
    try:
        c = r['concurso']
    except KeyError:
        return 'falha na chamada da API'
    
    str_acumulou = "\x02Acumulou!\x02 Sorteio {} ({}): [{}] - Próx. sorteio: {} - Valor acumulado: {}".format(
                        c['numero'],
                        c['data'],
                        ', '.join(r['concurso']['numeros_sorteados']),
                        r['proximo_concurso']['data'],
                        'R$ {}'.format(c['valor_acumulado'])
                    )
                    
    str_ganhador = "\x02{} {}!\x02 - Valor pago: R$ {} - Sorteio {} ({}): [{}] - Próx. sorteio: {} - Valor estimado: {}".format(
                        c['premiacao']['sena']['ganhadores'],
                        'Ganhadores' if int(c['premiacao']['sena']['ganhadores']) > 1 else 'Ganhador',
                        c['premiacao']['sena']['valor_pago'],
                        c['numero'],
                        c['data'],
                        ', '.join(r['concurso']['numeros_sorteados']),
                        r['proximo_concurso']['data'],
                        r['proximo_concurso']['valor_estimado'],
                    )
    
    return str_ganhador if c['premiacao']['sena']['ganhadores'] != '0' else str_acumulou
