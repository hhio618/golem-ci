import os
import yaml


def load_spec_file(context_dir):
    if os.path.exists(context_dir, yaml):
        with open(os.path.join(context_dir, yaml)) as spec_file:
            # The FullLoader parameter handles the conversion from YAML
            yaml_string = spec_file.read()
            # expand the yaml content from environment variables.
            expanded = os.path.expandvars(yaml_string)
            spec = yaml.safe_load(expanded)
            # TODO: validate spec here
            steps = spec['steps']
            if len(steps) == 0:
                print("There are no steps provided to the pipeline!")
                return None
            return spec
    else:
        return None