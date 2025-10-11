from multiprocessing import Pool

from core.helpers import zip_to_objects
from core.tools.ads import Ads
from utils import load_json, log_error, logger, sleep


class PhantomImport:
    def __init__(self, profile, label, password, seed_phrase):
        self.profile = profile
        self.ads = Ads(profile, wallet_type=Ads.WALLET_PHANTOM)
        self.label = label
        self.password = password
        self.seed_phrase = seed_phrase

    def execute(self):
        try:
            logger.info(f"Profile: {self.ads.label} | Phantom Import | Starting")

            self.ads.wallet.import_new(self.label, None, self.password, self.seed_phrase)

            logger.success(f"Profile: {self.ads.label} | Phantom Import | Imported Successfully")
            self.ads.close_browser()
            return True
        except Exception as e:
            log_error(e, f"Profile: {self.profile}")

            return False

    @staticmethod
    def run_profile(profile, label, password, seed_phrase, initial_delay):
        try:
            sleep(initial_delay)
            PhantomImport(profile, label, password, seed_phrase).execute()
        except Exception as e:
            log_error(e, f"Profile: {profile}")

    @classmethod
    def run(cls):
        instructions = load_json("modules/chore/phantom_import/instructions.json")

        profiles = instructions["profiles"]

        labels = zip_to_objects(profiles, instructions["labels"])
        passwords = zip_to_objects(profiles, instructions["passwords"])
        seed_phrases = zip_to_objects(profiles, instructions["seed_phrases"])

        if instructions["parallel_execution"]:
            try:
                pool = Pool(processes=instructions["max_processes"])

                for i, profile in enumerate(profiles):
                    pool.apply_async(
                        cls.run_profile,
                        args=(
                            profile,
                            labels[profile],
                            passwords[profile],
                            seed_phrases[profile],
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
                cls(profile, labels[profile], passwords[profile], seed_phrases[profile]).execute()
