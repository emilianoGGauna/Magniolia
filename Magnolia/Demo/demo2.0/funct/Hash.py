import bcrypt

class Hash:
    @staticmethod
    def hash_password(password):
        # Generate a bcrypt hash
        bcrypt_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return bcrypt_hash.decode()

    @staticmethod
    def verify_password(plain_password, hashed_password):
        # The hashed_password is expected to be a bcrypt hash in string format
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())