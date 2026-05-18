class Messages:

    token_invalid = "Token inválido, autorização negada."
    token_expired = "O token expirou. Faça login novamente."

    service_registered = "Serviço criado com sucesso!"
    service_name_exists = "Já existe um serviço com este nome."
    service_not_found = "Serviço não encontrado."
    service_deleted = "Serviço apagado com sucesso."
    service_updated = "Serviço atualizado com sucesso."
    service_not_found = "Serviço não encontrado."

    error_internal_server = "Ocorreu um erro inesperado nos nossos servidores. Por favor, tente novamente mais tarde."

    email_code_msg = "Bem-vindo! O seu código de verificação é:"
    email_verified_success = "Código aceite! O seu e-mail foi verificado com sucesso."
    email_code_expired = (
        "O código de verificação expirou após 5 minutos. Por favor, solicite um novo."
    )
    email_code_invalid = "Código de verificação inválido. Por favor, tente de novo."
    email_not_sent = (
        "Não foi possível enviar o e-mail de verificação. Verifique a sua ligação."
    )
    code_sent_success = "Um novo código foi enviado para o seu e-mail."

    password_reset_success = "A palavra-passe foi redefinida com sucesso."
    password_change_success = "A palavra-passe foi alterada com sucesso."


    login_success = "Login realizado com sucesso! Bem-vindo de volta."
    login_invalid_credentials = "Credenciais inválidas. Palavra-passe incorreta."
    login_not_found = "Credenciais inválidas. Utilizador não encontrado no sistema."
    login_unverified = (
        "Conta não verificada. Por favor, confirme o seu e-mail antes de poder entrar."
    )


    org_registered = "Organização e Administrador registados com sucesso!"
    org_name_exists = (
        "Já existe uma Organização com este nome. Por favor, escolha outro."
    )
    org_email_exists = "O e-mail indicado já está registado para uma Organização."
    org_phone_exists = "O telefone indicado já está registado para uma Organização."

 
    user_email_exists = "Já existe uma conta registada com esse e-mail."
    user_username_exists = (
        "O nome de utilizador já está em uso. Escolha uma alternativa."
    )
    user_phone_exists = "Já existe um utilizador registado com esse número de telefone."

    validation_invalid_email = (
        "O e-mail inserido é inválido. Verifique e tente novamente."
    )
    validation_invalid_phone = "O número de telefone inserido é inválido."
    validation_weak_password = (
        "Senha inválida. Use letras, números e caracteres difíceis."
    )

    queue_registered = "Cliente registado na fila com sucesso!"
    queue_no_counter = "Nenhum guichê disponível para este serviço."
    queue_service_not_found = "Serviço não encontrado nesta organização."
    client_already_in_queue = "Já existe um cliente com este nome na fila para este serviço."
    queue_deleted = "Cliente removido da fila com sucesso!"
    queue_not_found = "Cliente não encontrado na fila."

    organization_not_found = "Organização não encontrada."
    permission_denied = "Permissão negada."
