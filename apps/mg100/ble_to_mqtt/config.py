import canvas

class Config:
    def __init__(self, config_file="config.cb"):
        self.config_file = config_file
        self.config = {}

    def save(self):
        # Save the config dictionary to a CBOR file
        cbor = canvas.zcbor_from_obj(self.config, 0)
        if cbor is None:
            return

        # Try to open the file
        try:
            f = open(self.config_file, 'wb')
        except:
            print("Config: Could not open file {} for writing".format(
                self.config_file))
            return

        # Write the CBOR to the file
        f.write(cbor)
        f.close()

    def load(self):
        # Try to open the file
        try:
            f = open(self.config_file, 'rb')
        except:
            print("Config: Could not open file {} for reading".format(
                self.config_file))
            self.save()
            return

        # Read the contents of the file
        cbor = f.read()
        f.close()
        if cbor is None:
            return

        # Convert the CBOR to an object
        config_file = canvas.zcbor_to_obj(cbor)
        if config_file is None:
            self.save()
            return

        # Copy the contents of the config file to the config dictionary
        for c in config_file:
            self.config[c] = config_file[c]

    def get(self, key):
        if key in self.config:
            return self.config[key]
        return None

    def set(self, key, value):
        self.config[key] = value

    def dump(self):
        for k in self.config:
            print("{}: {}".format(k, self.config[k]))
