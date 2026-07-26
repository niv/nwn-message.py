from __future__ import annotations
import secrets


def _init_crc32_table() -> list[int]:
    result = []
    for i in range(256):
        value = i
        for _ in range(8):
            if value & 1:
                value = (value >> 1) ^ 0xEDB88320
            else:
                value = value >> 1
        result.append(value)
    return result


_CRC32_TABLE = _init_crc32_table()


class CDKey:
    """
    Represents a Neverwinter Nights CD key, with methods for validation,
    scrambling/unscrambling, and generation.

    Contains the private (secret) bits of a CD key, so make sure to keep
    instances of this class secure.
    """

    BASE26_CHARS = "UANPXTFWCQ9DVLE3GYJHK74R6M"
    PUBLIC_SIZE = 8
    PRIVATE_SIZE = 20
    CRC_SIZE = 7
    KEY_LENGTH = 41
    DASHES = 6

    def __init__(self, key: str):
        CDKey._validate_format(key)
        self._public, self._private, self._crc = CDKey._unscramble(key)
        expected_crc = CDKey._generate_crc(
            self._public.encode("ascii"), self._private.encode("ascii")
        )
        if expected_crc != self._crc:
            raise ValueError("Invalid CD key: CRC check failed")

    @staticmethod
    def _validate_format(key: str) -> None:
        if len(key) != CDKey.KEY_LENGTH:
            raise ValueError(
                f"Key must be {CDKey.KEY_LENGTH} characters long, got {len(key)}"
            )

        expected_dash_positions = [5, 11, 17, 23, 29, 35]
        for pos in expected_dash_positions:
            if key[pos] != "-":
                raise ValueError(f"Expected dash at position {pos + 1}")

        clean_key = key.replace("-", "")
        if not all(c in CDKey.BASE26_CHARS for c in clean_key):
            invalid_chars = set(clean_key) - set(CDKey.BASE26_CHARS)
            raise ValueError(
                f"Invalid characters in key: {', '.join(sorted(invalid_chars))}"
            )

        expected_char_count = CDKey.PRIVATE_SIZE + CDKey.PUBLIC_SIZE + CDKey.CRC_SIZE
        if len(clean_key) != expected_char_count:
            raise ValueError(
                f"Expected {expected_char_count} non-dash characters, got {len(clean_key)}"
            )

    @staticmethod
    def _unscramble(key: str) -> tuple[str, str, str]:
        clean_key = key.replace("-", "")

        private_chars = []
        crc_chars = []
        public_chars = []

        part = 0
        crc_start_point = CDKey.PRIVATE_SIZE - CDKey.CRC_SIZE - 1

        for char in clean_key:
            while True:
                if part == 0:
                    part = 1
                    if len(private_chars) < CDKey.PRIVATE_SIZE:
                        private_chars.append(char)
                        break

                if part == 1:
                    part = 2
                    if (
                        len(private_chars) > crc_start_point
                        and len(crc_chars) < CDKey.CRC_SIZE
                    ):
                        crc_chars.append(char)
                        break

                if part == 2:
                    part = 0
                    if len(public_chars) < CDKey.PUBLIC_SIZE:
                        public_chars.append(char)
                        break

                    # If public is full but private or crc still need chars, retry
                    if (
                        len(private_chars) < CDKey.PRIVATE_SIZE
                        or len(crc_chars) < CDKey.CRC_SIZE
                    ):
                        continue
                    break

        return "".join(public_chars), "".join(private_chars), "".join(crc_chars)

    @staticmethod
    def _generate_crc(pub_bytes: bytes, priv_bytes: bytes) -> str:
        crc_value = 0

        for b in pub_bytes:
            temp1 = (crc_value >> 8) & 0x00FFFFFF
            temp2 = _CRC32_TABLE[((crc_value ^ b) & 0xFF)]
            crc_value = temp1 ^ temp2

        for b in priv_bytes:
            temp1 = (crc_value >> 8) & 0x00FFFFFF
            temp2 = _CRC32_TABLE[((crc_value ^ b) & 0xFF)]
            crc_value = temp1 ^ temp2

        return CDKey._encode_base26_value(crc_value, CDKey.CRC_SIZE)

    def public_key(self) -> str:
        """
        The public part of the CD key (8 characters).
        """
        return self._public

    def full_key(self) -> str:
        """
        The full CD key in standard format (41 characters with dashes).

        THIS CONTAINS THE PRIVATE PART OF THE KEY. Do not share, do not send
        over untrusted connections or to untrusted endpoints.

        Returns:
            A string containing the full CD key.
        """
        return CDKey._scramble(self._public, self._private, self._crc)

    def __str__(self) -> str:
        return self.public_key()

    def __repr__(self) -> str:
        return f"CDKey(public={self.public_key()})"

    @staticmethod
    def _encode_base26_value(val: int, length: int) -> str:
        result = ""
        for _ in range(length):
            result = CDKey.BASE26_CHARS[val % 26] + result
            val //= 26
        return result

    @staticmethod
    def _scramble(public: str, private: str, crc: str) -> str:
        if len(public) != CDKey.PUBLIC_SIZE:
            raise ValueError(f"Public part must be {CDKey.PUBLIC_SIZE} characters")
        if len(private) != CDKey.PRIVATE_SIZE:
            raise ValueError(f"Private part must be {CDKey.PRIVATE_SIZE} characters")
        if len(crc) != CDKey.CRC_SIZE:
            raise ValueError(f"CRC part must be {CDKey.CRC_SIZE} characters")

        result = [""] * CDKey.KEY_LENGTH
        dashes = 0
        pi = si = ci = 0

        for idx in range(CDKey.KEY_LENGTH):
            if (idx + 1) % CDKey.DASHES == 0:
                result[idx] = "-"
                dashes += 1
            elif (idx + dashes) % 2 == 1 and pi < CDKey.PUBLIC_SIZE:
                result[idx] = public[pi]
                pi += 1
            elif (
                (idx + dashes) % 2 == 1
                and si > (CDKey.PRIVATE_SIZE - CDKey.CRC_SIZE - 1)
                and ci < CDKey.CRC_SIZE
            ):
                result[idx] = crc[ci]
                ci += 1
            elif si < CDKey.PRIVATE_SIZE:
                result[idx] = private[si]
                si += 1
            else:
                raise ValueError("Math error generating key")

        return "".join(result)

    @classmethod
    def generate(cls, public: str | None = None) -> CDKey:
        """
        Generate a new CD key with optional specified public part.

        If no public part is specified, a random one will be generated.

        These generated keys can be used for local testing, but will not work
        in multiplayer as they are not registered with the masterserver.

        Args:
            public (str | None): Optional public part of the key. Must be 8 characters
                long and only contain characters from BASE26_CHARS.

        Returns:
            CDKey: The generated CDKey instance.

        Raises:
            ValueError: If the provided public part is invalid.
        """

        def _generate_random_string(length: int) -> str:
            return "".join(secrets.choice(CDKey.BASE26_CHARS) for _ in range(length))

        if public is None:
            public = _generate_random_string(cls.PUBLIC_SIZE)
        elif len(public) != cls.PUBLIC_SIZE:
            raise ValueError(f"Public part must be {cls.PUBLIC_SIZE} characters")
        elif not all(c in cls.BASE26_CHARS for c in public):
            raise ValueError(
                f"Public part must only contain characters from: {cls.BASE26_CHARS}"
            )

        private = _generate_random_string(cls.PRIVATE_SIZE)

        pub_bytes = public.encode("ascii")
        priv_bytes = private.encode("ascii")
        crc = CDKey._generate_crc(pub_bytes, priv_bytes)
        return cls(cls._scramble(public, private, crc))
