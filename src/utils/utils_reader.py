import kaggle
import logging
import os

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log_reader = logging.getLogger("LOG-READER")


class Reader:

    # https://stackoverflow.com/questions/49386920/download-kaggle-dataset-by-using-python download di kaggle.json
    # bisogna aggiungere il file json in una cartella interna ".kaggle" sotto il proprio utente
    def __init__(self, dataset: str = "thoughtvector/customer-support-on-twitter"):
        """
        This function initialize a Reader Object in order to download dataset from kaggle
        :param dataset: kaggle's dataset to download
        """
        log_reader.info("Reader Creation ...")
        self.dataset = dataset
        log_reader.info("Reader Created")

    def download(self) -> None:
        """
        This function download dataset from kaggle into data/ folder
        :return: None
        """
        log_reader.info("Authentication Kaggle ...")
        kaggle.api.authenticate()
        log_reader.info("Authenticated Kaggle")

        log_reader.info("Downloading ...")
        kaggle.api.dataset_download_files(self.dataset, path='data/',
                                          unzip=True)
        log_reader.info("Downloaded")
