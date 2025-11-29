import dropbox
import json

class DropboxManager:

    ACCESS_TOKEN = "sl.u.AGKRanq1e92x-RlJiHoi2JSbFk0n_2Vh2cAnIpnAUpI3HYQO260-vKGiu6kuEqeJnbQEyahnOTuCeko9MeJankxEXW5zty3-LQnio5MUV297Tu1ttTU7Ijf9tfzNhbAtZalSiddnXjzs3dNP4u30A3SUXNUGRtm2fOrRHcnNUEXcAL57ChN5BJG_b9jtMB1cjNiXGeg6yX9jiGGMFjjuq8ngKiEhQNoCVztvuVsEvqI2KERoBUdMsavS7VIid-iLUGdAHAQ291fLqxVvpL3Hu1WccKu0A-miftyEyu5nlmSbSYQRi3tG9LI49XInofOxHldQIe68YaofjwC4eCKplj4QturqNK4VoDp5IR2RdGhEItnPsJoqbumtHyqhpYNvmqIaFR41i5vdyUrH-fOIP22ZsAzRccsMeR_kRBCgZmIFRGo2b4HAaG18k0jTuykFrSk9YTw4sXSwEbG7bni3DARXbAW6q-QiP7_7ezJibbYIGfqqZ3X9D9HE21Yiv2vyCw8x-f_IxhNOg20QMvjQd7II4FBMMLT86qboN1bxqe_cCu99N0SlHGUxI3qU8Rcg2LOuxdvQYRVuZFmAjY96F3jPEJb1BOD8dxn9e5bZ6UmVEGXUWi8AQTKv63BNloFDOH4PkkuU1jENu9QHNrVeQCr7PjaFPNevI5G-TQGnva-0qMArmfUvhOR-868EeLa9Ing74W1_kDOrfApKI0q_424OLK70_lqpRQZh-pEIgAtqgAQl6lgzwNdEtOthCqfi3yA8Vza7dW1gNIO93B47BOcBIOyv_Znh2oO3pABu9OZQuw7y0CzMjz_QYA8TBCeH3C1nC_jxvA-kMyoMqIL2y4PhhJfWByzUI8gdYo9JKWQbNmJuLCfrdN8_x1eeIpzI5IQHLcxPC9238UdXda7pwB2PsaVpD8P1fuY06JJbDRbBOu0qgj_ZX7e5Vhe3OU5L-3amqt6NimHAnCmEzOU-Xa3KijjX0ReNjkWPeQgJeM-xyfxdZ6PoOr9mWJ7UBi3nrHCvgq6Ut2IcjXMWKCSOF3Cbh8Ti-8DnktbrQvwt6HTW6Yupi-UIdwI1qn68IGwK7m6GU8OI3bR3Y6djC5jQqcZlLGJABKY0lgyAR35XE0vZz4U1rK6sLkyZWU8Q2Fa-r6-q7gUmp6OcnV4_bwk7cvjWuW6hNn-ZOCsd6UJRGx5P5yk5ONE3LOvzVAJve1fjb7DsFOQnHAPSPPJWiIDnNrj9hDKUL9DT-TfErAFKrDf7epnWdPLsoIZFp9unbztslJYO_HsPgIFlYAClSw8lO5ZI0LTkRlqO5CZ4X2xaXyyu1lHWHQvqar2AKBB9m-oOMdygRAYwr3MXmphlyRlIXwS6oJMLcZk-zM7e4mwNvneAC0urg-zxR0vuDpGZQlbUtRElakOg5XGkV0X-dRwpu8xu"   # ⚠️ Usa el mismo que ya tenías
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
