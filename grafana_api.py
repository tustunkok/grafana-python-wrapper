import logging
import requests
from urllib.parse import urlparse

class GrafanaAPI:
    def __init__(self, url: str, token: str, verify: bool=True) -> None:
        logger = logging.getLogger('grafana_api')
        logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler('grafana_api.log')
        file_handler.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)

        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(hostname)s | %(message)s')

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        self._logger = logging.LoggerAdapter(logger, {'hostname': urlparse(url).hostname})
        self.url = url
        self._token = token
        self._verify = verify


    def _enrich_error_response(self, response: requests.Response, message: str) -> dict:
        if len(response.content) == 0:
            self._logger.warning('Empty response returned.')
            return {'customStatusCode': response.status_code}

        if response.status_code != 200:
            response_dict = response.json()
            response_dict['customStatusCode'] = response.status_code
            self._logger.warning(f'The request returns a non 200 status code: {response.status_code}')
            return response_dict

        self._logger.info(message)
        return response.json()


    def create_dashboard(self, additional_data: dict, folder_id: int=None, folder_uid: str=None, message: str=None, overwrite: bool=None) -> dict:
        payload = additional_data.copy()

        if folder_id is not None:
            payload['folderId'] = folder_id
        
        if folder_uid is not None:
            payload['folderUid'] = folder_uid
        
        if message is not None:
            payload['message'] = message
        
        if overwrite is not None:
            payload['overwrite'] = overwrite

        response = requests.post(
            f'{self.url}/api/dashboards/db',
            headers={'Authorization': f'Bearer {self._token}'},
            json=payload,
            verify=self._verify
        )

        return self._enrich_error_response(response, f'Dashboard created with the name {additional_data["dashboard"]["title"]}.')


    def get_dashboard_by_uid(self, uid: str) -> dict:
        response = requests.get(
            f'{self.url}/api/dashboards/uid/{uid}',
            headers={'Authorization': f'Bearer {self._token}'},
            verify=self._verify
        )

        return self._enrich_error_response(response, f'Dashboard with UID {uid} is found.')


    def delete_dashboard_by_uid(self, uid: str) -> dict:
        response = requests.delete(
            f'{self.url}/api/dashboards/uid/{uid}',
            headers={'Authorization': f'Bearer {self._token}'},
            verify=self._verify
        )

        return self._enrich_error_response(response, f'Dashboard with UID {uid} deleted successfully.')


    def get_all_dashboards(self) -> dict:
        response = requests.get(
            f'{self.url}/api/search?type=dash-db',
            headers={'Authorization': f'Bearer {self._token}'},
            verify=self._verify
        )

        return self._enrich_error_response(response, 'All dashboards are returned.')


    def get_all_datasources(self) -> dict:
        response = requests.get(
            f'{self.url}/api/datasources',
            headers={'Authorization': f'Bearer {self._token}'},
            verify=self._verify
        )

        return self._enrich_error_response(response, 'All datasources are returned.')


    def get_datasource_by_uid(self, uid: str) -> dict:
        response = requests.get(
            f'{self.url}/api/datasources/uid/{uid}',
            headers={'Authorization': f'Bearer {self._token}'},
            verify=self._verify
        )

        return self._enrich_error_response(response, f'Datasource with UID {uid} is returned.')


    def get_datasource_by_name(self, name: str) -> dict:
        response = requests.get(
            f'{self.url}/api/datasources/name/{name}',
            headers={'Authorization': f'Bearer {self._token}'},
            verify=self._verify
        )

        return self._enrich_error_response(response, f'Datasource with the name {name} is returned.')


    def create_datasource(self, name: str, type_: str, url: str, access: str='proxy', additional_data: dict=None) -> dict:
        payload = { 'name': name, 'type': type_, 'url': url, 'access': access }

        if additional_data is not None:
            payload.update(additional_data)

        response = requests.post(
            f'{self.url}/api/datasources/',
            headers={'Authorization': f'Bearer {self._token}'},
            json=payload,
            verify=self._verify
        )

        return self._enrich_error_response(response, f'The datasource with the name {name} is created.')


    def delete_datasource_by_uid(self, uid: str) -> dict:
        response = requests.delete(
            f'{self.url}/api/datasources/uid/{uid}',
            headers={'Authorization': f'Bearer {self._token}'},
            verify=self._verify
        )

        return self._enrich_error_response(response, f'The datasource with UID {uid} is deleted.')


    def get_datasource_health_by_uid(self, uid: str) -> dict:
        response = requests.get(
            f'{self.url}/api/datasources/uid/{uid}/health',
            headers={'Authorization': f'Bearer {self._token}'},
            verify=self._verify
        )

        return self._enrich_error_response(response, 'Datasource health is returned.')


    def get_all_folders(self, limit: int=1000) -> dict:
        response = requests.get(
            f'{self.url}/api/folders?limit={limit}',
            headers={'Authorization': f'Bearer {self._token}'},
            verify=self._verify
        )

        return self._enrich_error_response(response, 'All folders are returned.')


    def get_folder_by_uid(self, uid: str) -> dict:
        response = requests.get(
            f'{self.url}/api/folders/{uid}',
            headers={'Authorization': f'Bearer {self._token}'},
            verify=self._verify
        )

        return self._enrich_error_response(response, f'The folder with UID {uid} is returned.')


    def create_folder(self, title: str, uid: str=None) -> dict:
        payload = dict()

        if uid is not None:
            payload['uid'] = uid
        
        payload['title'] = title

        response = requests.post(
            f'{self.url}/api/folders',
            headers={'Authorization': f'Bearer {self._token}'},
            json=payload,
            verify=self._verify
        )

        return self._enrich_error_response(response, f'A folder with the title {title} is created.')


    def delete_folder_by_uid(self, uid: str) -> dict:
        response = requests.delete(
            f'{self.url}/api/folders/{uid}',
            headers={'Authorization': f'Bearer {self._token}'},
            verify=self._verify
        )

        return self._enrich_error_response(response, f'The folder with UID {uid} is deleted.')
