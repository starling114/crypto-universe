from multiprocessing import Pool

from core.helpers import zip_to_objects
from core.tools.ads import Ads
from utils import load_json, log_error, logger, sleep


class RabbyImport:
    def __init__(self, profile, label, address, password, private_key):
        self.profile = profile
        self.ads: Ads = Ads(profile)
        self.label = label
        self.address = address
        self.password = password
        self.private_key = private_key

    def execute(self):
        try:
            logger.info(f"Profile: {self.ads.label} | Rabby Import | Starting")

            self.ads.wallet.import_new(self.label, self.address, self.password, self.private_key)

            logger.success(f"Profile: {self.ads.label} | Rabby Import | Imported Successfully")
            self.ads.close_browser()
            return True
        except Exception as e:
            log_error(e, f"Profile: {self.profile}")

            return False

    @staticmethod
    def run_profile(profile, label, address, password, private_key, initial_delay):
        try:
            sleep(initial_delay)
            RabbyImport(profile, label, address, password, private_key).execute()
        except Exception as e:
            log_error(e, f"Profile: {profile}")

    @classmethod
    def run(cls):
        instructions = load_json("modules/chore/rabby_import/instructions.json")

        profiles = instructions["profiles"]

        labels = zip_to_objects(profiles, instructions["labels"])
        addresses = zip_to_objects(profiles, instructions["addresses"])
        passwords = zip_to_objects(profiles, instructions["passwords"])
        private_keys = zip_to_objects(profiles, instructions["private_keys"])

        if instructions["parallel_execution"]:
            try:
                pool = Pool(processes=instructions["max_processes"])

                for i, profile in enumerate(profiles):
                    pool.apply_async(
                        cls.run_profile,
                        args=(
                            profile,
                            labels[profile],
                            addresses[profile],
                            passwords[profile],
                            private_keys[profile],
                            (i % instructions["max_processes"]) * 5,
                        ),
                    )

                pool.close()
                pool.join()
            except KeyboardInterrupt as e:
                pool.terminate()
                pool.join()
                logger.info("All parallel processes are terminated.")
                raise e
        else:
            for i, profile in enumerate(profiles):
                cls(profile, labels[profile], addresses[profile], passwords[profile], private_keys[profile]).execute()
