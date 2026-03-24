from fastapi import APIRouter, status

router = APIRouter()

@router.get("get-admin-data")
def get_admin_data():
    pass

@router.post("register-costumer", status_code=status.HTTP_201_CREATED)
def register_costumer():
    pass

@router.put("block-costumer", status_code=status.HTTP_423_LOCKED)
def block_costumer():
    pass

@router.delete("delete-costumer", status_code=status.HTTP_200_OK)
def delete_costumer():

    pass

@router.post("add-services", status_code=status.HTTP_201_CREATED)
def register_costumer():
    pass


@router.patch("set-clock", status_code=status.HTTP_201_CREATED)
def set_clock():
    pass

@router.get("generate-history", status_code=status.HTTP_201_CREATED)
def register_costumer():
    pass