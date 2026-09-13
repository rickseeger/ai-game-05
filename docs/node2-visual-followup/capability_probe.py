import json
import sys
sys.path.insert(0, '/usr/local/lib/hermes-agent')
from dotenv import load_dotenv
load_dotenv('/root/.hermes/.env')
from tools.vision_tools import check_vision_requirements
from hermes_cli.config import load_config
config = load_config()
print(json.dumps({
    'vision_requirements': check_vision_requirements(),
    'vision_config': {k: v for k, v in config.get('auxiliary', {}).get('vision', {}).items() if k in ('provider', 'model', 'timeout')},
    'main_model': config.get('model', {}).get('default'),
    'main_provider': config.get('model', {}).get('provider'),
}, indent=2))
