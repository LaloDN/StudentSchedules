def model_to_dict(model):
    model_dict = model.__dict__
    del model_dict['_sa_instance_state']
    return model_dict