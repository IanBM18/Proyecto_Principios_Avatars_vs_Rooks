import dropbox
import json

class DropboxManager:

    ACCESS_TOKEN = "sl.u.AGJF3Z2ow6TrWvGv1onwXniqqBoFSErPIaH2dwzKs3nMIF6C8aCfnKxB8VMIqiovWdjgULw72Cw7Z1sKvP69_00_gThm3q0YsjAPgMdAc5ZDP3p3B6BTnfE6tiyufxAWQVsC6k0sPMnsdu-dAW-oD08mQWeOsYz-cBYYPKllzYG0iBa9OsygaIBldL6hpquH7RSslMwZ32ULGCvkhwY4Bk1AXam5stPuRrvu1tgMPzVoNIhsa99DBO1AMfPHpV4gfB3dNylJPaazU6UZFytOBB7IDQvNge-5gBwHpIz_CsWc5dGz-XI-eJL2q_Hznf2fXl3HE5IGQYo1pic68M3_EIpk26_9EghgGFofxkJXh0jF1OGV5VGsFZ3aaa7PcOQU_QtEZ6FfEwG6zvKQ1Jtb3-9mXae_pO8RNY7ZLT2x-PtSfp0ZNpctycC79HWnXEZ8fNmDNwgEEQn52rG0zuQ8FxF5Qkv4jhNsstm1NYHDt2VxPGUkEC4S7KPtC4W9BzScEOAZB1A9XG_dXQlpdp31zNRmq5-6KP8_p6TW1CoAe6fZ6qBD1Ej_UZCrao7GdzlDcjaaNmqYTXrxkYj3DQogZQCBD6s9LjYNn-k5v1KFQEZlF4kifhrAmxTDU10i6hLDjgtf2XsME-6PJenF8cSYgfNbAtPtYsBkcXEm1DzrTDln32YDjfP6zA2QujLTPXnOBmA-5QNqZIf4aAFKWP2gF_5KL47hIOXRT_DjA02CF5anLHcUac10jDMtEm4XLYkC7NZ2-RdXhzlQ_nwAhwJdFGwCLZSHJ-B4En0ZNCPCncP6Hwwuda3Nf0hXxuFTbwBw109LsaHIqtcFeFAeyWwDDQLoHNPEvWMS9EdngczLv2MDV25zQkCxRoFL52NOZ1W53fC7Vd-iZZ3ZjUImqbF_y14ppg_HZGGIXnc-pnyGiSH_77ezGUeQJ7PV4eE5idWG6lWURkBaFF7icwWYZpfQSv0_Z0iDnZg0pRzglMJoD29tLaazoXdJFm-Ln_2Iuef2z6fuOZMOXQ4XmPZnFZVXO8o4M19NDCirNSd9Vgm60C0BS_Xh0G-8d0j6idikLF19uvKQ9vFOOqi7I5S9mKzP_V8Wkaf0Z95uo272xF08U6C689WowJ9fOzaCe49Mf50aRwVHnfMjEDc-Fq6Eld8wNNFYwMaxqlaCLif3IyGT9GL1W6oCukbUCLA5dqVRoRC-nyMfPB0NgPfrwpYntgYlDfmw-1vfY35mt8bLi9Fbej6TqSBg-XIj2tUnVcJ_MP6VpKh5VrCvhS2ByLJAUjJs0sy00kYtm8ZcU1QGrqXM4op9EIirW46km0PafdkSTPcWfV0HYMEX_ad3RLzOX8wlpY8hdPmxKsZw4JgQEbLyqjTYdmqstUmcgE8XQsIL6VpfW7ShqO_6fWjFsH-Ck5kx6ra4drl1rwiIYbUHVIO64PrvZFPWD9YnubjaOW4FMnWkHDc"   # ⚠️ Usa el mismo que ya tenías
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
