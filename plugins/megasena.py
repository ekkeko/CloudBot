from cloudbot import hook
import json, urllib, urllib.request
import locale

@hook.command("megasena",autohelp=False)
def mega(message, bot, conn):
    request = urllib.request.Request(bot.config.get("api_keys", {}).get("megasena_url", None), headers={'Cookie': 'security=true; path=/'})
    megasena = json.loads(urllib.request.urlopen(request).read().decode('utf8'))
    
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    
    if megasena['ganhadores'] == 0:
        message('(Concurso {} - {})  {}  Acumulou: {}'.format(megasena['concurso'],
                                                     megasena['dataStr'], 
                                                     megasena['resultadoOrdenado'], 
                                                     locale.currency(megasena['valor_acumulado'], grouping=True)))
    else:
        message('(Concurso {} - {})  {}  Ganhado{}: {} Premio: {}'.format( megasena['concurso'], 
                                                                  megasena['dataStr'], 
                                                                  megasena['resultadoOrdenado'], 
                                                                  'res' if megasena['ganhadores'] > 1 else 'r', 
                                                                  megasena['ganhadores'], 
                                                                  locale.currency(megasena['valor'], grouping=True) ))
