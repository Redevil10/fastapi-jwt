from config import settings

DEFAULT_SUPER_USER = {
    "id": 1,
    "username": settings.DEFAULT_SUPERUSER_USERNAME,
    "email": settings.DEFAULT_SUPERUSER_EMAIL,
    "full_name": settings.DEFAULT_SUPERUSER_FULL_NAME,
    "is_active": True,
    "is_superuser": True,
}

TEST_USER_1 = {
    "id": 2,
    "username": "testuser1",
    "email": "test.user1@example.com",
    "full_name": "Test User1",
    "is_active": True,
    "is_superuser": False,
}
TEST_USER_1_PASSWORD = "dummypass"

TEST_USER_2 = {
    "id": 3,
    "username": "testuser2",
    "email": "test.user2@example.com",
    "full_name": "Test User2",
    "is_active": True,
    "is_superuser": True,
}
TEST_USER_2_PASSWORD = "superpass"


TEST_USER_1_NEW = {
    "id": 2,
    "username": "testuser1_new",
    "email": "test_user1@example.com",
    "full_name": "TEST USER1 NEW",
    "is_active": True,
    "is_superuser": False,
}
TEST_USER_1_NEW_PASSWORD = "newpass"


def test_create_default_superuser(test_app):
    response = test_app.post("/users/init")
    assert response.status_code == 200
    assert response.json() == DEFAULT_SUPER_USER

    # try to create_default_superuser_again
    test_data = {"detail": "Email already registered"}
    response = test_app.post("/users/init")
    assert response.status_code == 400
    assert response.json() == test_data


def login(test_app, username, password):
    login_data = {
        "username": username,
        "password": password,
    }
    response = test_app.post("/users/token", data=login_data)
    assert response.status_code == 200
    return response.json()


def super_user_login(test_app):
    return login(
        test_app,
        settings.DEFAULT_SUPERUSER_USERNAME,
        settings.DEFAULT_SUPERUSER_PASSWORD,
    )


def test_create_access_token(test_app):
    r = super_user_login(test_app)
    assert "access_token" in r
    assert r["token_type"] == "bearer"


def test_get_user_me(test_app):
    access_token = super_user_login(test_app)["access_token"]
    response = test_app.get(
        "/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200

    assert response.json() == DEFAULT_SUPER_USER


def test_create_normal_user(test_app):
    access_token = super_user_login(test_app)["access_token"]
    test_data = TEST_USER_1.copy()
    test_data["password"] = TEST_USER_1_PASSWORD
    response = test_app.post(
        "/users",
        headers={"Authorization": f"Bearer {access_token}"},
        json=test_data,
    )
    assert response.status_code == 200
    assert response.json() == TEST_USER_1


def test_create_super_user(test_app):
    access_token = super_user_login(test_app)["access_token"]
    test_data = TEST_USER_2.copy()
    test_data["password"] = TEST_USER_2_PASSWORD
    response = test_app.post(
        "/users",
        headers={"Authorization": f"Bearer {access_token}"},
        json=test_data,
    )
    assert response.status_code == 200
    assert response.json() == TEST_USER_2


def test_get_user_by_email_normal_user(test_app):
    access_token = login(test_app, TEST_USER_1["username"], TEST_USER_1_PASSWORD)[
        "access_token"
    ]
    response = test_app.get(
        "/users",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"email": TEST_USER_1["email"]},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "The user doesn't have enough privileges"}


def test_get_user_by_email_superuser(test_app):
    access_token = super_user_login(test_app)["access_token"]
    response = test_app.get(
        "/users",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"email": TEST_USER_1["email"]},
    )
    assert response.status_code == 200
    assert response.json() == TEST_USER_1

    response = test_app.get(
        "/users",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"email": DEFAULT_SUPER_USER["email"]},
    )
    assert response.status_code == 200
    assert response.json() == DEFAULT_SUPER_USER


def test_get_user_by_id_normal_user(test_app):
    access_token = login(test_app, TEST_USER_1["username"], TEST_USER_1_PASSWORD)[
        "access_token"
    ]
    response = test_app.get(
        "/users",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"user_id": TEST_USER_1["id"]},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "The user doesn't have enough privileges"}


def test_get_user_by_id_superuser(test_app):
    access_token = super_user_login(test_app)["access_token"]
    response = test_app.get(
        "/users",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"user_id": TEST_USER_1["id"]},
    )
    assert response.status_code == 200
    assert response.json() == TEST_USER_1

    response = test_app.get(
        "/users",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"user_id": DEFAULT_SUPER_USER["id"]},
    )
    assert response.status_code == 200
    assert response.json() == DEFAULT_SUPER_USER


def test_get_user_by_username_normal_user(test_app):
    access_token = login(test_app, TEST_USER_1["username"], TEST_USER_1_PASSWORD)[
        "access_token"
    ]
    response = test_app.get(
        "/users",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"username": TEST_USER_1["username"]},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "The user doesn't have enough privileges"}


def test_get_user_by_username_superuser(test_app):
    access_token = super_user_login(test_app)["access_token"]
    response = test_app.get(
        "/users",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"username": TEST_USER_1["username"]},
    )
    assert response.status_code == 200
    assert response.json() == TEST_USER_1

    response = test_app.get(
        "/users",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"username": DEFAULT_SUPER_USER["username"]},
    )
    assert response.status_code == 200
    assert response.json() == DEFAULT_SUPER_USER


def test_update_user_normal_user(test_app):
    """
    TODO:
    1. normal user can only update their own data
    2. test email, username, password update
    """
    access_token = login(test_app, TEST_USER_1["username"], TEST_USER_1_PASSWORD)[
        "access_token"
    ]
    test_data = {
        "email": "test.user1@example.com",
        "full_name": "TEST USER1 NEW",
        "is_active": True,
        "is_superuser": False,
    }
    new_data = TEST_USER_1.copy()
    new_data.update(test_data)

    response = test_app.put(
        f"/users/{TEST_USER_1['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json=test_data,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "The user doesn't have enough privileges"}


def test_update_user_super_user(test_app):
    """superuser should be able to update any user"""
    access_token = super_user_login(test_app)["access_token"]
    test_data = {
        "email": "test.user1@example.com",
        "full_name": "TEST USER1 SUPER deactivated",
        "is_active": False,
        "is_superuser": True,
    }
    new_data = TEST_USER_1.copy()
    new_data.update(test_data)

    response = test_app.put(
        f"/users/{TEST_USER_1['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json=test_data,
    )
    assert response.status_code == 200
    assert response.json() == new_data

    test_data = TEST_USER_1_NEW.copy()
    test_data["password"] = TEST_USER_1_NEW_PASSWORD

    response = test_app.put(
        f"/users/{TEST_USER_1['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json=test_data,
    )
    assert response.status_code == 200
    assert response.json() == TEST_USER_1_NEW


def test_get_user_all_normal_user(test_app):
    access_token = login(
        test_app, TEST_USER_1_NEW["username"], TEST_USER_1_NEW_PASSWORD
    )["access_token"]
    response = test_app.get(
        "/users/all", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "The user doesn't have enough privileges"}


def test_get_user_all_super_user(test_app):
    access_token = super_user_login(test_app)["access_token"]
    response = test_app.get(
        "/users/all", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    test_data = [
        DEFAULT_SUPER_USER,
        TEST_USER_1_NEW,
        TEST_USER_2,
    ]
    assert response.json() == test_data


def test_delete_user_normal_user(test_app):
    """can a user delete itself?"""
    access_token = login(
        test_app, TEST_USER_1_NEW["username"], TEST_USER_1_NEW_PASSWORD
    )["access_token"]
    response = test_app.delete(
        f"/users/{TEST_USER_1_NEW['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "The user doesn't have enough privileges"}


def test_delete_user_super_user(test_app):
    access_token = super_user_login(test_app)["access_token"]

    # delete normal user
    response = test_app.delete(
        f"/users/{TEST_USER_1_NEW['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    correct_response = TEST_USER_1_NEW.copy()
    correct_response["status"] = "deleted"
    correct_response.pop("id")
    assert response.json() == correct_response

    # delete super user
    response = test_app.delete(
        f"/users/{TEST_USER_2['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    correct_response = TEST_USER_2.copy()
    correct_response["status"] = "deleted"
    correct_response.pop("id")
    assert response.json() == correct_response


def test_get_user_all_again(test_app):
    access_token = super_user_login(test_app)["access_token"]
    response = test_app.get(
        "/users/all", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json() == [DEFAULT_SUPER_USER]
