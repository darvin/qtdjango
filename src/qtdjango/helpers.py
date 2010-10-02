
def get_registered_models(models):
    ms =[]
    for url, model in models.items():
        model.resource_name = url
        ms.append(model)
    return ms
    

