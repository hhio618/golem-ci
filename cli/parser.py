import os
import yaml


def load_spec_file(context_dir):
    spec_pathes = [os.path.join(context_dir, ".golem-ci.yml"), os.path.join(context_dir, ".golem-ci.yaml")]
    spec_exists = [os.path.exists(path) for path in spec_pathes]
    if False in spec_exists and True in spec_exists:
        with open(spec_pathes[spec_exists.index(True)]) as spec_file:
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
       print("Please either provide a .golem-ci.yml or a .golem-ci.yaml")
       return None
