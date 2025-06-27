import re
from typing import Dict, Any, List, Optional
from rapidfuzz import fuzz, process

class SpringBootServiceExtractor:
    """
    Extracts service information from Spring Boot YAML configurations using fuzzy matching
    """
    
    def __init__(self):
        # Define field patterns with synonyms for fuzzy matching
        self.field_patterns = {
            'service_name': [
                'spring.application.name',
                'application.name',
                'app.name',
                'service.name',
                'name',
                'servicename',
                'applicationname',
                'appname'
            ],
            'port': [
                'server.port',
                'port',
                'serverport',
                'application.port',
                'app.port'
            ],
            'protocol': [
                'protocol',
                'scheme',
                'transport',
                'server.protocol'
            ],
            'dependent_services': [
                'external-services',
                'external.services',
                'dependencies.services',
                'dependentservices',
                'services',
                'microservices',
                'external'
            ],
            'dependent_infrastructure': [
                'datasource',
                'redis',
                'rabbitmq',
                'kafka',
                'activemq',
                'database',
                'cache',
                'queue',
                'messaging',
                'infrastructure'
            ]
        }
        
        # Infrastructure patterns to identify
        self.infrastructure_patterns = {
            'postgresql': ['postgresql', 'postgres', 'psql', 'jdbc:postgresql'],
            'mysql': ['mysql', 'mariadb', 'jdbc:mysql'],
            'redis': ['redis', 'lettuce'],
            'rabbitmq': ['rabbitmq', 'amqp'],
            'kafka': ['kafka', 'bootstrap-servers'],
            'activemq': ['activemq', 'broker-url'],
            'mongodb': ['mongodb', 'mongo'],
            'elasticsearch': ['elasticsearch', 'es']
        }
    
    def extract_service_info(self, yaml_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract service information from Spring Boot YAML configuration (direct structure traversal)
        """
        docs = []
        if len(yaml_data) > 1 and any(key.startswith('document_') for key in yaml_data.keys()):
            for key, doc in yaml_data.items():
                if key.startswith('document_'):
                    docs.append(doc)
        else:
            docs = [yaml_data]

        # Aggregated results
        service_names = set()
        versions = set()
        ports = []  # Use list to preserve order
        dependent_services = []
        dependent_infrastructure = []
        profiles = set()
        protocol = None

        for doc in docs:
            spring = doc.get('spring', {})
            # Service name and version
            app = spring.get('application', {})
            if 'name' in app:
                service_names.add(app['name'])
            if 'version' in app:
                versions.add(app['version'])
            # Port (main service port)
            if 'server' in spring and 'port' in spring['server']:
                port_val = spring['server']['port']
                port_number = self.extract_port_number(port_val)
                if port_number and port_number not in ports:
                    ports.append(port_number)
                elif port_val not in ports:
                    ports.append(port_val)
            # Protocol: look for SSL/HTTPS config
            if 'server' in spring and 'ssl' in spring['server']:
                protocol = 'https'
            elif 'server' in spring and 'servlet' in spring['server']:
                if not protocol:
                    protocol = 'http'
            # Profile
            if 'profiles' in spring and 'active' in spring['profiles']:
                profiles.add(spring['profiles']['active'])
            # Dependent services (external-services)
            ext_services = spring.get('app', {}).get('external-services', {})
            for svc_name, svc_details in ext_services.items():
                dependent_services.append({'name': svc_name, 'details': svc_details})
            # Kafka topics as services
            kafka_topics = spring.get('app', {}).get('kafka-topics', {})
            for topic_name, topic_details in kafka_topics.items():
                dependent_services.append({'name': topic_name, 'type': 'kafka-topic', 'details': topic_details})
            # Queues as services
            queues = spring.get('app', {}).get('queues', {})
            for queue_name, queue_details in queues.items():
                dependent_services.append({'name': queue_name, 'type': 'queue', 'details': queue_details})
            # Dependent infrastructure: datasource
            datasource = spring.get('datasource', {})
            for dbtype, dbval in datasource.items():
                if isinstance(dbval, dict):
                    dependent_infrastructure.append({'type': dbtype, 'details': dbval})
            # Redis
            if 'redis' in spring:
                dependent_infrastructure.append({'type': 'redis', 'details': spring['redis']})
            # RabbitMQ
            if 'rabbitmq' in spring:
                dependent_infrastructure.append({'type': 'rabbitmq', 'details': spring['rabbitmq']})
            # Kafka
            if 'kafka' in spring:
                dependent_infrastructure.append({'type': 'kafka', 'details': spring['kafka']})
            # ActiveMQ
            if 'activemq' in spring:
                dependent_infrastructure.append({'type': 'activemq', 'details': spring['activemq']})

        # If protocol still not set, look for any SSL/HTTPS/secure keys in all docs
        if not protocol:
            for doc in docs:
                spring = doc.get('spring', {})
                if 'server' in spring and 'ssl' in spring['server']:
                    protocol = 'https'
                    break
            if not protocol:
                protocol = 'http'

        # Debug: print found ports
        print(f"[ServiceExtractor] Found service ports: {ports}")

        # Compose result
        return {
            'service_name': {'value': next(iter(service_names), None)},
            'version': next(iter(versions), None),
            'port': {'value': ports[0]} if ports else None,
            'protocol': {'value': protocol},
            'profiles': list(profiles),
            'dependent_services': dependent_services,
            'dependent_infrastructure': dependent_infrastructure,
            'additional_data': {}
        }
    
    def flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary for easier searching"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Handle lists by creating indexed keys
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        items.extend(self.flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
                    else:
                        items.append((f"{new_key}[{i}]", item))
            else:
                items.append((new_key, v))
        return dict(items)
    
    def find_best_match(self, target_field: str, data_keys: List[str], threshold: int = 70) -> Optional[tuple]:
        """Find the best fuzzy match for a field"""
        patterns = self.field_patterns.get(target_field, [target_field])
        
        best_match = None
        best_score = 0
        
        for pattern in patterns:
            match = process.extractOne(
                pattern,
                data_keys,
                scorer=fuzz.ratio,
                score_cutoff=threshold
            )
            
            if match and match[1] > best_score:
                best_match = match
                best_score = match[1]
        
        return best_match
    
    def extract_service_name(self, flat_data: Dict[str, Any]) -> Optional[str]:
        """Extract service name using fuzzy matching"""
        match = self.find_best_match('service_name', list(flat_data.keys()))
        if match:
            field_name, confidence = match[:2]
            value = flat_data[field_name]
            return {
                'value': str(value),
                'matched_field': field_name,
                'confidence': confidence
            }
        return None
    
    def extract_port(self, flat_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract port information"""
        match = self.find_best_match('port', list(flat_data.keys()))
        if match:
            field_name, confidence = match[:2]
            value = flat_data[field_name]
            
            # Extract port number from various formats
            port_number = self.extract_port_number(value)
            
            return {
                'value': port_number,
                'matched_field': field_name,
                'confidence': confidence,
                'original_value': value
            }
        return None
    
    def extract_port_number(self, value: Any) -> Optional[str]:
        """Extract port number from various formats"""
        if isinstance(value, (int, str)):
            port_str = str(value)
            # Handle environment variable format like "${SERVER_PORT:8080}"
            env_match = re.search(r'\$\{.*?:(\d+)\}', port_str)
            if env_match:
                return env_match.group(1)
            
            # Extract first number found
            number_match = re.search(r'\d+', port_str)
            if number_match:
                return number_match.group()
        
        return None
    
    def extract_protocol(self, flat_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract protocol information"""
        # For Spring Boot, protocol is usually HTTP/HTTPS based on context
        # Check for SSL/TLS configurations
        ssl_indicators = ['ssl', 'https', 'tls', 'security']
        
        for key in flat_data.keys():
            if any(indicator in key.lower() for indicator in ssl_indicators):
                return {
                    'value': 'https',
                    'matched_field': key,
                    'confidence': 80,
                    'reason': 'SSL/TLS configuration detected'
                }
        
        # Default to HTTP for Spring Boot applications
        return {
            'value': 'http',
            'confidence': 90,
            'reason': 'Default protocol for Spring Boot'
        }
    
    def extract_dependent_services(self, flat_data: Dict[str, Any], docs=None) -> List[Dict[str, Any]]:
        """Extract dependent services from all known keys and all documents"""
        services = []
        # Always look for external-services in all docs
        if docs:
            for doc in docs:
                app = doc.get('spring', {}).get('app', {})
                ext_services = None
                # Try both app.external-services and app['external-services']
                if 'external-services' in doc.get('spring', {}).get('app', {}):
                    ext_services = doc['spring']['app']['external-services']
                elif 'external-services' in doc.get('spring', {}):
                    ext_services = doc['spring']['external-services']
                if ext_services and isinstance(ext_services, dict):
                    for name, details in ext_services.items():
                        services.append({'name': name, 'details': details})
                # Also look for kafka-topics
                if 'kafka-topics' in doc.get('spring', {}).get('app', {}):
                    for name in doc['spring']['app']['kafka-topics'].keys():
                        services.append({'name': name, 'type': 'kafka-topic'})
        # Fallback to fuzzy match
        if not services:
            match = self.find_best_match('dependent_services', list(flat_data.keys()))
            if match:
                field_name, confidence = match[:2]
                value = flat_data[field_name]
                if isinstance(value, list):
                    services.extend([{'name': str(v)} if not isinstance(v, dict) else v for v in value])
                elif isinstance(value, dict):
                    services.extend([{'name': k, 'details': v} for k, v in value.items()])
                else:
                    services.append({'name': str(value)})
        return services
    
    def extract_dependent_infrastructure(self, flat_data: Dict[str, Any], docs=None) -> List[Dict[str, Any]]:
        """Extract dependent infrastructure from all known keys and all documents"""
        matches = []
        # Always look for infra in all docs
        infra_keys = ['datasource', 'redis', 'rabbitmq', 'kafka', 'activemq']
        if docs:
            for doc in docs:
                spring = doc.get('spring', {})
                for infra in infra_keys:
                    if infra in spring:
                        infra_val = spring[infra]
                        if isinstance(infra_val, dict):
                            # For datasource, may have primary/secondary
                            if infra == 'datasource':
                                for dbtype, dbval in infra_val.items():
                                    if isinstance(dbval, dict):
                                        matches.append(self.extract_infrastructure_details(f'{infra}.{dbtype}', dbval, dbtype if dbtype in ['primary','secondary'] else infra))
                            else:
                                matches.append(self.extract_infrastructure_details(infra, infra_val, infra))
        # Fallback to fuzzy/flat
        if not matches:
            for infra_type, patterns in self.infrastructure_patterns.items():
                for pattern in patterns:
                    for key, value in flat_data.items():
                        if pattern in key.lower() or (isinstance(value, str) and pattern in value.lower()):
                            matches.append(self.extract_infrastructure_details(key, value, infra_type))
            match = self.find_best_match('dependent_infrastructure', list(flat_data.keys()))
            if match:
                field_name, confidence = match[:2]
                value = flat_data[field_name]
                matches.append(self.extract_infrastructure_details(field_name, value, 'custom'))
        return matches
    
    def extract_infrastructure_details(self, key: str, value: Any, infra_type: str) -> Dict[str, Any]:
        """Extract specific details for infrastructure components"""
        details = {}
        
        if infra_type == 'postgresql' or infra_type == 'mysql':
            if isinstance(value, dict):
                details = {
                    'url': value.get('url', ''),
                    'username': value.get('username', ''),
                    'driver': value.get('driver-class-name', ''),
                    'pool_size': value.get('hikari', {}).get('maximum-pool-size', '')
                }
        
        elif infra_type == 'redis':
            if isinstance(value, dict):
                details = {
                    'host': value.get('host', ''),
                    'port': value.get('port', ''),
                    'database': value.get('database', ''),
                    'timeout': value.get('timeout', '')
                }
        
        elif infra_type == 'rabbitmq':
            if isinstance(value, dict):
                details = {
                    'host': value.get('host', ''),
                    'port': value.get('port', ''),
                    'username': value.get('username', ''),
                    'virtual_host': value.get('virtual-host', '')
                }
        
        elif infra_type == 'kafka':
            if isinstance(value, dict):
                details = {
                    'bootstrap_servers': value.get('bootstrap-servers', ''),
                    'consumer_group': value.get('consumer', {}).get('group-id', ''),
                    'producer_config': value.get('producer', {})
                }
        
        return details
    
    def extract_additional_data(self, flat_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract additional service data"""
        additional = {
            'version': None,
            'profiles': [],
            'endpoints': [],
            'queues': [],
            'kafka_topics': []
        }
        
        # Extract version
        for key, value in flat_data.items():
            if 'version' in key.lower():
                additional['version'] = value
        
        # Extract profiles
        for key, value in flat_data.items():
            if 'profiles.active' in key.lower():
                additional['profiles'] = [value] if isinstance(value, str) else value
        
        # Extract management endpoints
        for key, value in flat_data.items():
            if 'management.endpoints.web.exposure.include' in key.lower():
                if isinstance(value, str):
                    additional['endpoints'] = [ep.strip() for ep in value.split(',')]
                elif isinstance(value, list):
                    additional['endpoints'] = value
        
        # Extract queues
        for key, value in flat_data.items():
            if 'queues' in key.lower() and isinstance(value, dict):
                additional['queues'] = list(value.keys())
        
        # Extract Kafka topics
        for key, value in flat_data.items():
            if 'kafka-topics' in key.lower() and isinstance(value, dict):
                additional['kafka_topics'] = list(value.keys())
        
        return additional 