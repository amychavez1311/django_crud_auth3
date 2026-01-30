"""
Almacenamiento personalizado para usar Azure Blob Storage en Django
Esto permite guardar TODOS los archivos de medios (fotos, certificados, etc.) en Azure
"""

from django.conf import settings
from django.core.files.storage import Storage
from io import BytesIO
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
import os


class AzureBlobStorage(Storage):
    """
    Almacenamiento personalizado que usa Azure Blob Storage
    Reemplaza el almacenamiento local de Django con Azure
    """
    
    def __init__(self):
        self.connection_string = getattr(settings, 'AZURE_STORAGE_CONNECTION_STRING', '')
        self.container_name = getattr(settings, 'AZURE_STORAGE_MEDIA_CONTAINER', 'media')
        self.account_name = self._get_account_name()
        
    def _get_account_name(self):
        """Extrae el nombre de la cuenta del connection string"""
        try:
            for part in self.connection_string.split(';'):
                if part.startswith('AccountName='):
                    return part.split('=')[1]
        except:
            pass
        return ''
    
    def _get_blob_client(self, name):
        """Obtiene un cliente de blob"""
        blob_service_client = BlobServiceClient.from_connection_string(
            self.connection_string
        )
        
        # Crear contenedor si no existe
        try:
            blob_service_client.get_container_client(self.container_name).get_container_properties()
        except:
            blob_service_client.create_container(self.container_name)
        
        blob_client = blob_service_client.get_blob_client(
            container=self.container_name,
            blob=name
        )
        return blob_client
    
    def _save(self, name, content):
        """Guarda un archivo en Azure"""
        try:
            blob_client = self._get_blob_client(name)
            
            # Leer el contenido si es un objeto archivo
            if hasattr(content, 'read'):
                content_data = content.read()
            else:
                content_data = content
            
            # Subir el blob
            blob_client.upload_blob(content_data, overwrite=True)
            return name
            
        except Exception as e:
            print(f"Error guardando archivo en Azure: {e}")
            raise
    
    def _open(self, name, mode='rb'):
        """Abre un archivo desde Azure"""
        try:
            blob_client = self._get_blob_client(name)
            download_stream = blob_client.download_blob()
            file_content = download_stream.readall()
            return BytesIO(file_content)
        except Exception as e:
            print(f"Error abriendo archivo en Azure: {e}")
            raise
    
    def delete(self, name):
        """Elimina un archivo de Azure"""
        try:
            blob_client = self._get_blob_client(name)
            blob_client.delete_blob()
        except Exception as e:
            print(f"Error eliminando archivo de Azure: {e}")
    
    def exists(self, name):
        """Verifica si un archivo existe en Azure"""
        try:
            blob_client = self._get_blob_client(name)
            blob_client.get_blob_properties()
            return True
        except:
            return False
    
    def listdir(self, path):
        """Lista archivos en un directorio de Azure"""
        try:
            blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
            container_client = blob_service_client.get_container_client(self.container_name)
            
            directories = []
            files = []
            
            for blob in container_client.list_blobs(name_starts_with=path):
                files.append(blob.name)
            
            return directories, files
        except Exception as e:
            print(f"Error listando archivos: {e}")
            return [], []
    
    def size(self, name):
        """Obtiene el tamaño de un archivo"""
        try:
            blob_client = self._get_blob_client(name)
            properties = blob_client.get_blob_properties()
            return properties.size
        except:
            return 0
    
    def url(self, name):
        """Obtiene la URL pública de un archivo"""
        try:
            # Construir la URL manualmente si es posible
            if self.account_name:
                base_url = f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{name}"
                
                # Si se requiere SAS token para acceso privado
                if getattr(settings, 'AZURE_STORAGE_USE_SAS', False):
                    sas_token = generate_blob_sas(
                        account_name=self.account_name,
                        container_name=self.container_name,
                        blob_name=name,
                        account_key=self._get_account_key(),
                        permission=BlobSasPermissions(read=True),
                        expiry=datetime.utcnow() + timedelta(days=365)
                    )
                    return f"{base_url}?{sas_token}"
                else:
                    return base_url
            else:
                # Fallback: usar la URL del blob client
                blob_client = self._get_blob_client(name)
                if getattr(settings, 'AZURE_STORAGE_USE_SAS', False):
                    sas_token = generate_blob_sas(
                        account_name=self.account_name,
                        container_name=self.container_name,
                        blob_name=name,
                        account_key=self._get_account_key(),
                        permission=BlobSasPermissions(read=True),
                        expiry=datetime.utcnow() + timedelta(days=365)
                    )
                    return f"{blob_client.url}?{sas_token}"
                else:
                    return blob_client.url
                
        except Exception as e:
            print(f"Error obteniendo URL: {e}")
            return ''
    
    def _get_account_key(self):
        """Extrae la clave de la cuenta del connection string"""
        try:
            for part in self.connection_string.split(';'):
                if part.startswith('AccountKey='):
                    return part.split('=')[1]
        except:
            pass
        return ''
