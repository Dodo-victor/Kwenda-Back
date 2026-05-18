from fastapi import APIRouter, Depends, status, HTTPException
from middleware.location_middlware import location_middleware
from sqlalchemy.orm import Session
from sqlalchemy import or_
from core.database.db import get_db
from core.database.tables import User, Organization, UserOrganization, VerificationCode
from schemas.user_schema import (
    UserSchema,
    LoginRequest,
    ResendVerificationRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
)
from schemas.organization_schema import OrganizationSchema
from core.utilis.security import hash_password, verify_password, verify_reset_code
from core.utilis.generate_token import gnerate_token
from core.utilis.validate_inpust import ValidateInputs
import uuid
from datetime import datetime, timedelta
from core.services import email_server
from schemas.organization_schema import RegisterUserOrganizationRequest
from core.utilis.security import generate_code_verification
from core.utilis.messages import Messages
from middleware.check_email import check_email


router = APIRouter()


@router.post("/check-user", status_code=status.HTTP_201_CREATED)
def register_user(
    user_schema: UserSchema,
    db: Session = Depends(get_db),
    # current_location=Depends(location_middleware),
):
    try:
        # Step 1: validate inputs
        validate_inputs = ValidateInputs()

        user_db = db.query(User).filter(User.email == user_schema.email).first()

        if user_db:
            raise HTTPException(400, "Já existe uma conta cadastrada com este e-mail!")

        organiztion_db = (
            db.query(Organization)
            .filter(Organization.admin_id == uuid.UUID(user_schema.id))
            .first()
        )
        if not organiztion_db:
            return HTTPException(
                206,
                "Registro incompleto, por favor registre a sua organização.",
                headers={
                    "title": "Registro Incompleto",
                    "content": "Voce não concluiu com o seu registro, por favor insira os dados de sua organização",
                },
            )

        else:
            if ValidateInputs.validate_email(email=user_schema.email) == False:
                raise HTTPException(400, "E-mail inválido, tente outro.")

            if (
                ValidateInputs.validate_phone_number(
                    phone_number=user_schema.phone_number
                )
                == False
            ):
                raise HTTPException(
                    400, "Número de telefone inválido, verifique e tenta novamente."
                )
            if ValidateInputs.validate_password(user_schema.password) == False:
                raise HTTPException(
                    400,
                    "Senha inválida. A senha deve ter pelo menos 8 caracteres, incluir letras maiúsculas, minúsculas, números e caracteres especiais. Exemplo: steip$Wo",
                )
            # uid = str(uuid.uuid4())
            # userdata = User(
            #   id=uid,
            #  organization_id=None,
            # username=user_schema.username,
            # email=validate_inputs.validate_email(user_schema.email),
            # address=user_schema.address,
            # phone_number=validate_inputs.validate_phone_number(
            #   user_schema.phone_number
            # ),
            # password=validate_inputs.validate_password(user_schema.password),
            # is_active=True,
            # type_user="user",
            # created_at=datetime.utcnow(),
            # last_login=datetime.utcnow(),
            # )

            # db.add(userdata)
            # db.commit()
            # db.refresh(userdata)

            # token = gnerate_token(userdata.id)

            return {"next_step": True}
        # Step 5: generate token

        # Step 6: return token

    except HTTPException as http_exc:
        db.rollback()
        match http_exc.detail:
            case "Já existe uma conta cadastrada com este e-mail!":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=http_exc.detail,
                )
            case "E-mail inválido, tente outro.":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=http_exc.detail,
                )
            case "Senha inválida. A senha deve ter pelo menos 8 caracteres, incluir letras maiúsculas, minúsculas, números e caracteres especiais. Exemplo: steip$Wo":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=http_exc.detail,
                )
            case "Já existe um usuario com este email.":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=http_exc.detail,
                )
            case "Registro incompleto, por favor registre a sua organização.":
                raise http_exc

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/register-user-and-organization", status_code=status.HTTP_201_CREATED)
async def register_organization(
    user_organiztion_and_user_request: RegisterUserOrganizationRequest,
    db: Session = Depends(get_db),
    current_location=Depends(location_middleware),
):
    try:
        # VERIFICATIONS

        check_name_org = (
            db.query(Organization)
            .filter(
                Organization.name == user_organiztion_and_user_request.organization.name
            )
            .first()
        )

        if check_name_org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Messages.org_name_exists,
            )

        check_phone_org = (
            db.query(Organization)
            .filter(
                Organization.phone_number
                == user_organiztion_and_user_request.organization.phone_number
            )
            .first()
        )
        if check_phone_org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Messages.org_phone_exists,
            )

        org_db = (
            db.query(Organization)
            .filter(
                Organization.email
                == user_organiztion_and_user_request.organization.email
            )
            .first()
        )
        if org_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Messages.org_email_exists,
            )
        else:
            validate_input = ValidateInputs()
            if (
                validate_input.validate_email(
                    user_organiztion_and_user_request.organization.email
                )
                == False
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=Messages.validation_invalid_email,
                )

            if (
                validate_input.validate_phone_number(
                    user_organiztion_and_user_request.organization.phone_number
                )
                == False
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=Messages.validation_invalid_phone,
                )

            if (
                validate_input.validate_password(
                    user_organiztion_and_user_request.admin.password
                )
                == False
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=Messages.validation_weak_password,
                )

            # get location user from back-end
            # save logo and get from claudianary

            # save user and organization

            uid = str(uuid.uuid4())
            userdata = User(
                id=uid,
                username=user_organiztion_and_user_request.admin.username,
                email=user_organiztion_and_user_request.admin.email,
                address=user_organiztion_and_user_request.admin.address,
                phone_number=user_organiztion_and_user_request.admin.phone_number,
                password=validate_input.validate_password(
                    user_organiztion_and_user_request.admin.password
                ),
                is_active=True,
                type_user="user",
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow(),
            )

            """ db.add(userdata)
            db.commit()
            db.refresh(userdata) """

            organization_data = Organization(
                name=user_organiztion_and_user_request.organization.name,
                email=validate_input.validate_email(
                    user_organiztion_and_user_request.organization.email
                ),
                phone_number=validate_input.validate_phone_number(
                    user_organiztion_and_user_request.organization.phone_number
                ),
                province=(
                    current_location
                    if current_location
                    else user_organiztion_and_user_request.organization.province
                ),
                city=user_organiztion_and_user_request.organization.city,
                type_organization=user_organiztion_and_user_request.organization.type_organization,
                address=user_organiztion_and_user_request.organization.address,
                website=user_organiztion_and_user_request.organization.website,
                admin_id=uid,
                logo="",
            )
            db.add_all([userdata, organization_data])
            db.commit()
            db.refresh(userdata)
            db.refresh(organization_data)
            db.flush()
            # generate code verification
            code = generate_code_verification()

            # save code verification
            verification_code = VerificationCode(
                code=code,
                user_id=uid,
                organization_id=organization_data.id,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(minutes=5),
            )
            db.add(verification_code)
            db.commit()
            db.refresh(verification_code)

            # send_email from email from organization
            valid_email = validate_input.validate_email(
                user_organiztion_and_user_request.organization.email
            )
            await email_server.send_email(
                body=f"{Messages.email_code_msg} {code} usa este código para verificcar o seu e-mail.",
                subject="Código de verificação",
                email=valid_email,
            )

            return {"next_step": True}

            # comment:
        # end if

    except HTTPException as http_exc:
        db.rollback()
        raise http_exc
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/verify-email", status_code=status.HTTP_200_OK)
def verify_email(paylod_data: dict = Depends(check_email)):
    try:
        token = gnerate_token(dict(paylod_data))
        return {"message": Messages.email_verified_success, "token": token}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{Messages.error_internal_server}, {e}")
    # end try


@router.post("/login", status_code=status.HTTP_200_OK)
def user_login(login_request: LoginRequest, db: Session = Depends(get_db)):
    try:
        identifier = login_request.identifier.strip()
        is_email = "@" in identifier

        if is_email:
            user = db.query(User).filter(User.email == identifier).first()
        else:
            user = db.query(User).filter(User.phone_number == identifier).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=Messages.login_not_found,
            )

        is_pwd_valid = verify_password(login_request.password, bytes(user.password))

        if not is_pwd_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=Messages.login_invalid_credentials,
            )

        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=Messages.login_unverified,
            )

        token = gnerate_token(str(user.id))

        user.last_login = datetime.utcnow()
        db.commit()

        return {
            "message": Messages.login_success,
            "token": token,
            "type_user": user.type_user,
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error in login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Messages.error_internal_server,
        )


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
async def resend_verification(
    request: ResendVerificationRequest, db: Session = Depends(get_db)
):
    try:
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=Messages.login_not_found
            )

        if user.is_verified:
            return {"message": "A conta já está verificada."}

        # Delete old codes
        db.query(VerificationCode).filter(VerificationCode.user_id == user.id).delete()

        # Need organization_id for the VerificationCode model
        org = db.query(Organization).filter(Organization.admin_id == user.id).first()
        if not org:
            assoc = (
                db.query(UserOrganization)
                .filter(UserOrganization.user_id == user.id)
                .first()
            )
            if not assoc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Utilizador não tem organização.",
                )
            org_id = assoc.organization_id
        else:
            org_id = org.id

        code = generate_code_verification()
        verification_code = VerificationCode(
            code=code,
            user_id=user.id,
            organization_id=org_id,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=5),
        )
        db.add(verification_code)
        db.commit()

        await email_server.send_email(
            [user.email], "Código de Verificação", f"{Messages.email_code_msg} {code}"
        )
        return {"message": Messages.code_sent_success}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Messages.error_internal_server,
        )


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    request: ForgotPasswordRequest, db: Session = Depends(get_db)
):
    try:
        identifier = request.identifier.strip()
        is_email = "@" in identifier

        if is_email:
            user = db.query(User).filter(User.email == identifier).first()
        else:
            user = db.query(User).filter(User.phone_number == identifier).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=Messages.login_not_found
            )

        org = db.query(Organization).filter(Organization.admin_id == user.id).first()
        if not org:
            assoc = (
                db.query(UserOrganization)
                .filter(UserOrganization.user_id == user.id)
                .first()
            )
            if not assoc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Utilizador não tem organização.",
                )
            org_id = assoc.organization_id
        else:
            org_id = org.id

        # Delete old codes
        db.query(VerificationCode).filter(VerificationCode.user_id == user.id).delete()

        code = generate_code_verification()
        verification_code = VerificationCode(
            code=code,
            user_id=user.id,
            organization_id=org_id,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=5),
        )
        db.add(verification_code)
        db.commit()

        if user.email:
            await email_server.send_email(
                [user.email],
                "Recuperação de Palavra-Passe",
                f"O seu código temporário de recuperação é: {code}",
            )
        return {"message": "Código de recuperação enviado. Verifique o seu e-mail."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Messages.error_internal_server,
        )


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        user_id = verify_reset_code(request.code, db)
        if user_id == "expired":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Messages.email_code_expired,
            )
        elif not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Messages.email_code_invalid,
            )

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=Messages.login_not_found
            )

        hashed_pw = hash_password(request.new_password)
        user.password = hashed_pw
        db.commit()

        return {"message": Messages.password_reset_success}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Messages.error_internal_server,
        )


@router.patch("/change-password", status_code=status.HTTP_200_OK)
def change_password(request: ChangePasswordRequest, db: Session = Depends(get_db)):
    try:
        identifier = request.identifier.strip()
        is_email = "@" in identifier

        if is_email:
            user = db.query(User).filter(User.email == identifier).first()
        else:
            user = db.query(User).filter(User.phone_number == identifier).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=Messages.login_not_found
            )

        is_pwd_valid = verify_password(request.old_password, bytes(user.password))
        if not is_pwd_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Palavra-passe antiga incorreta.",
            )

        hashed_pw = hash_password(request.new_password)
        user.password = hashed_pw
        db.commit()

        return {"message": Messages.password_change_success}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Messages.error_internal_server,
        )
