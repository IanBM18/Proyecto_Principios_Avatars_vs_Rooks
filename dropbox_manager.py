import dropbox
import json

class DropboxManager:

    ACCESS_TOKEN = "sl.u.AGJhEKDkqL1HkQMw3dzlVVNsmyWdhJPy0GeTLy4lyB1x7mdL0eGHzylxSdmL33mmFK9PAgvfE31tmx0ZhywN0QcvAVCPvo-nxCEMXXQVe1251sV8FFwBRHrEHXivu0GwOE2x5SaucTnnD0cK2VqeuUqwl3PkdjI7usmxiMNOLtR1wIOKtCxmeMfWztEfs9To4vrnzG9WVyfZNu7RmPSSmur1xdSaLQTr-dfrHIMDjPiLdsj7dCrpI8ctCSquF7p2NwuzXUrtIRjDwebd98xvWz8-cj_-MqzoTfTQ7TbF2E1xHq3NCLYTJ3JQ4KV-46um1xGLL3GQu_3Md3DxfRnvgPSICH_DnVUgZxJZY97tThh02KS6pqHYMwhwBEJh-4nXlOn4dh39knaGeYeb0SAKLGf01ZnZIkgy_rsDoy8LEH6v3JK0C5k6AffzNzCSoIrMLgiXPavp7TFmJna9bSe7Sgp4QLKXenNZItOPohsxMfN8e3Aht-DZdFCRki3Wmr4sEZEYrqXPofU6q8376hdXM2CkYuaCF0uLxWDs8ZqqSC9rBq0C2fSCUBaEBNRyDB_GKabLQb99LMm0ycj4uyBYK3DjrxPlSSq03Idgy9bFzivS0cicyDOqJlvBOgLzsY2U7GxMPDXswa17fJdV1Ll7ME4QDbw8xsUFt6tVmfGPvCL07Tjyo_9UUGfQ-WxGan1I9XiTTr_0OF6U7IBSZzwoX1zw78VDVMLxAOD0aLeBwKD9_nIMEZGZ_KUUAs5h4odFRUmitNuvym_BMMIBPmnBjq0wieU3DrX9grlaEzN7gz4BEs4QnfCB735AQjdBWvW0Ufz4GaaDlBZW2tZs4oQ6iYLNwLsDRzyXnGFWDKE0alTbWp8LaVYSL8UHW0T6UEbT9VBrMKwq6A1IEltsew8edOy5Q7tKTsZWrmLBpq9ZEMA5RRUzvOGS8SZVAu2ndEZwBApDill1-krCH5TqtXmrJ79mLwHiWisvTOtqoDzHYtRSkG4esiDCAPYFBQsEkIESqqwbyk4ZcHfQ2fjU6kECr1F3MVC1Uo4Nwx5Gt_kCdRKoTZLcowi0H39HoLQpEKV0duD7hmeNUx5ugOnpkCjp_qXf2n7mZLh1buTK8mHuBjsfyIvawe6QFk0_WrFqyZ8avLmJLBfYSNawhVxMoPtII3an1AH3TYNUcHpgV2TDSKYvruoNKTB5g6ObeoL0hFl2Ignhwen2eUgDe8wwK1m3IoVea9TjyxhZFTfnOsmUHRskhROpTh2SoFrJWScizoVi7u_FnnPO4N6wiaeTIlpDZ5tYrOcX1UAIhHBXQpBtSymoc_IyD5TtJGK5k8FZxToX3umP4JmKueR9zrkvDL7BpmTnXSM-grgBux5xd3QZvFqUCfwtgU42di1ehzTkoOWhzTerKGccDjwz2nbB-Hrcf8KB"   # ⚠️ Usa el mismo que ya tenías
    # =========================
    #   OBTENER CLIENTE DROPBOX
    # =========================
    @staticmethod
    def get_client():
        return dropbox.Dropbox(DropboxManager.ACCESS_TOKEN)

    # =========================
    #   DESCARGAR ARCHIVO JSON
    # =========================
    @staticmethod
    def descargar_json(nombre_archivo, default_type=list):
        dbx = DropboxManager.get_client()
        ruta = f"/avatars_vs_rooks/{nombre_archivo}"

        try:
            metadata, res = dbx.files_download(ruta)
            data = res.content.decode("utf-8")
            contenido = json.loads(data)

            # Asegurar tipo correcto (lista o dict)
            if default_type is list and isinstance(contenido, dict):
                return []
            if default_type is dict and isinstance(contenido, list):
                return {}

            return contenido

        except dropbox.exceptions.ApiError:
            return default_type()

    # =========================
    #   SUBIR ARCHIVO JSON
    # =========================
    @staticmethod
    def subir_json(nombre_archivo, data):
        dbx = DropboxManager.get_client()
        ruta = f"/avatars_vs_rooks/{nombre_archivo}"
        contenido = json.dumps(data, indent=4)

        dbx.files_upload(
            contenido.encode("utf-8"),
            ruta,
            mode=dropbox.files.WriteMode.overwrite
        )

    # =========================
    #   USUARIOS: CARGAR / GUARDAR
    # =========================
    @staticmethod
    def load_users():
        return DropboxManager.descargar_json("usuarios.json", default_type=list)

    @staticmethod
    def save_users(data):
        DropboxManager.subir_json("usuarios.json", data)

    # =========================
    #   SALÓN DE LA FAMA
    # =========================
    @staticmethod
    def load_scores():
        return DropboxManager.descargar_json("salon_fama.json", default_type=list)

    @staticmethod
    def upload_scores(data):
        DropboxManager.subir_json("salon_fama.json", data)
