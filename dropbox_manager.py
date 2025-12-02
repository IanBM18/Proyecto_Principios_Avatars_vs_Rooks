import dropbox
import json

class DropboxManager:

    ACCESS_TOKEN = "sl.u.AGIEtkg9Jn_w3XLjDkhPHY8nXsrpEpiWmNnqPl4GQMg6w8k8x2giEwzBFuJYIuRMn_0FiciGo8G2CiW97jAyTN7n2ekID-3IJIB2_zzEUfwd8BTfBp7qtwr4Fi9L7ma03nOup9aDD39NgDiOm7Py83VciPeR-qYNvE5j0XTJs993Cm207gv9udvSDqF1XCZd_RZ886J7vnJkgS06HwHiIBAAwTykQzgfV1L9CRekJvRmLgs5jaMLGg-JBZMD4hDMTeOFtxDNKuM3-ZKCIT2JmQwTEGWCY1acBMKjYLDX3qkVIQyPXmGatb89sSRSubDcNTRlhk3n7JxavptUNkUeB-xmLxDRmTAGknNOjDuKNPYPltV6L6fe_2caKmdJjtEkrz1sEPSuWbL-xf8dZRsmeFJTAxQWRNa-D0rNaM38dLlT0bENRyvJZvC1h6hPTw_RYdAsM2-lP_ZvOtxWSiFGoz_f1d1FPZuXv3H9o6FMqzTxVTWO7VIBQFVgUZogkgnHsD-OsKKEtb3qeIKqPk79mL1r2S2iJRjUrkqklN2Su-_PylyVP7hDFhyhcwXcpazz3_lW_-RWTgSFzAsujiSDOEtN52bzLVmYWrmnyTg2cW1VPP0xGr0VWtl_crqGj0RattwTbA0s5Uy5sxjGXiWP3_I1izteS9NA_v0wpO0Q1gsmN09Z8mr7Cg1cUCB1QDJWrQbcInPGZcrmIFtsWbx0Gip4MGympjDPRosSuN2DleZHbFSq2MCeHHp2u_uqqHOX_RaCfvBjIWDhiwe6iklFWR6gJMdAhVAZ769f2faNyuaubEeg4Ea38d6XyVLbhiY8zumOh_viSFsqLiTX2dSW50NG6UGyVoNXq-VgsztUnVOaxakwtkrmM0P_9v44dF2JMQMB3me9R6ONjmOUfKKnZaYBvjOKUdpD2UJkrMvzL2J2riU2Mpi12jQL-GTMYjoSTExwrHj3LkftaZTyF6Gn5hjsZRTPS_m03XVv-empx8dPtNx6mhbGh4fCUubA5oVpZd1eN2zKlbUgTDLrEplYFcuAu74b5W4jsUEcmRSP12qmM9kHtrKsdObMwNRbXCqRUkrqQCuST-74cAhamLe7i9OlGtXKAf135KXmd0YYhe8HCIj_391K5syET8fHrHgmCYCeUlZKndiG78OdGz_nsDbJMLcwA-J15GCVTFDqis7bx5vByasJlHxOQR1Gpz7PirN43jR1g6YtrEZ8xipMXe9NF9owbHJQfCkmmbuNCaZjVsyMWhdMPAFWm92fdBKrhljwoTFoLUODNepRK73z9XtDAnj5R5cqxdHtEQaJ2mzhnYwnOh_T9gv6b767w6w7TR2-okyNiS9FWdT5CJfSWieUzbElx-bdizj9HadyWk9lunl62_ujRAiYEC4_F2b_VxXMjR_3A9QMNO19OCfhSdCwQbl2Jqrjt-AbGquQOGSAoVLE_uzSmWXGQ0fcNtv8lCw"   # ⚠️ Usa el mismo que ya tenías
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
