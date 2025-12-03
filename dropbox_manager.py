import dropbox
import json

class DropboxManager:

    ACCESS_TOKEN = "sl.u.AGJoyBxYYQIv1yer2oRdxxegaf53YgI5h572g7Sy3bZuFX_xzth8aQ4OImHVKfsYF8_F8RicGYTjpPTU6gE0YXQSUDLwL3x-wiEEIPKnjm5VNqkJBbYEIWmXejGLLiEMevdRqt9-XMa6RPbKwaXBDD98aXiZxMXg-69rgz4-bpLiWHq9VvpFdNJ-0XxgoRmD2Js7mKQN8njSySswe0fyJ5thN9b3qmTOaT3gME8y0S4ZTB6pPKWVMUBvbjRpR9-R7uEBPM0mDi0iLuF1usq3ghGdDLbCWEJeKNvkSlNPDXolxQNVmKB_kipdHDjWpLxWtGMB6UoUBf-fe-etwT2lRLM3WOGBBiuclJPTZC7KOQYy-runz5IfWhubnoLrpL3FpmG-vXsmhyaDOJPxVdbXpN-qodETSglzF9JpwXHGvY8sQS71JwVAKVD5YOIjEX696onpeKtDV0hyatIPsCmPzpSzj3p2yd_3AbLAcHl4lqwaEOUUv4PrNzILtJKZC7gypOB-KXNNgDVMUpdyfwOZLslo3NrVtpAfw88o8_Cmn3m0o2MhRlZB06Y2FJ0L_1R9rQVyHsJAcrCIYFXEBDlxm_fGDCucW9GThpacSXioWN65d5818T7tMrSQ6T8m5GzGZJiVc_M7EecDNC2EyK2qQvKcZa8F5C9yWPweEoUVax9JjXoQRWoFQQUASA-W3BK_NWfDNJwDweDEvkyaaO2G8Zj8hoyCoKTCdZW-JORw5Jin9M3dnz_C2DR5b4d2YQo-iLXchYgz9WzGmbPg5U2G0cfvxaOpFUj1JsnS3wQUtkov0hTC1iuClygo15EwXRSb-kMR-NkdIOPFiJeUKpE5ILBTWHljZhEf0YigqkdKBDtxZodYBNAIQ3YjStvNjAxULoRoaXt59pW5OAuqU0ARU6y5riEHxVvEAoP8rOfWIyn-o34-nQa-REfOmBCq7kVBYzsuoVYyc7nFxzlBPmKJifov0H2FbCnaJzah2z3dNKTdARS9Dj-AFya8qR6tybvA44u1lsFbUS3zQ8cPBTmq6kfXlyamw0qAfM_BxE3xdq9OusQfwa_67MC2whVvav8jYbTZMWkJEiqSCG1iaulMzd1FuUXGehW3pGS7DYW0COxnFkcGBh8LenniCE6hfhuqFMQsJnYXXthzXvgtAwt5LyRryYbN5oqtd5z1ECZ9BwKGsXAbrTEE5XKkHKjgYAz6rUyQAbH8cGUiYVsSQ94x9IQwvFGBMH4Gkn1CRgwYE38x9QwV3JAssLZmKMxN-LyWu0CoenK4AVAMGsSVLyq0Z4-58_1XC2B8QOcekqjyGT6nDFt0DuVKInIJP9hhxd-jkuI5bYJYwWpbmTQXPrwi3C-xX_q7Dh1WZBKWycoxAfMaP_6ydd9Rw1lF2s9BKq0aRY4_dkEGxtroCoe0-E_t_p4pcOJ5VBgG-QjiZ1Cc4sTb3UZ3QEkAM1T-m74pMiPKoEQ"   # ⚠️ Usa el mismo que ya tenías
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
