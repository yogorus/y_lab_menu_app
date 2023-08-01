import pytest

# from tests.conftest import client
from httpx import AsyncClient
from tests.test_menu import create_menu, delete_menu

base_url = "http://localhost/api/v1"


@pytest.fixture(scope="session")
async def create_submenu(client: AsyncClient, create_menu):
    sent_json = {"title": "My submenu 1", "description": "My submenu description 1"}
    response = await client.post(
        f"/menus/{create_menu['id']}/submenus/", json=sent_json
    )
    assert response.status_code == 201
    response_json = response.json()
    assert "id" in response_json
    assert sent_json["title"] == response_json["title"]
    assert sent_json["description"] == response_json["description"]

    yield response_json


@pytest.fixture(scope="session")
async def patch_submenu(client: AsyncClient, create_menu, create_submenu):
    sent_json = {
        "title": "My updated submenu 1",
        "description": "My updated submenu description 1",
    }
    response = await client.patch(
        f"/menus/{create_menu['id']}/submenus/{create_submenu['id']}",
        json=sent_json,
    )
    assert response.status_code == 200

    response_json = response.json()
    assert create_submenu["id"] == create_submenu["id"]
    assert create_submenu["title"] != response_json["title"]
    assert create_submenu["description"] != response_json["description"]

    assert sent_json["title"] == response_json["title"]
    assert sent_json["description"] == response_json["description"]

    yield response_json


@pytest.fixture(scope="session")
async def delete_submenu(client: AsyncClient, create_menu, patch_submenu):
    response = await client.delete(
        f"/menus/{create_menu['id']}/submenus/{patch_submenu['id']}"
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"

    yield {"id": patch_submenu["id"]}


# No submenus
async def test_emtpy_submenu_list(client: AsyncClient, create_menu):
    response = await client.get(f"/menus/{create_menu['id']}/submenus/")
    assert response.status_code == 200
    assert response.json() == []


# After submenu is created
async def test_submenu_list_after_create(
    client: AsyncClient, create_menu, create_submenu
):
    response = await client.get(f"/menus/{create_menu['id']}/submenus/")
    assert response.status_code == 200
    assert len(response.json()) > 0


async def test_submenu_by_id_after_create(
    client: AsyncClient, create_menu, create_submenu
):
    response = await client.get(
        f"/menus/{create_menu['id']}/submenus/{create_submenu['id']}"
    )
    assert response.status_code == 200
    assert response.json() == create_submenu


# After update
async def test_updated_submenu_by_response(
    client: AsyncClient, create_menu, patch_submenu
):
    response = await client.get(
        f"/menus/{create_menu['id']}/submenus/{patch_submenu['id']}"
    )
    assert response.status_code == 200
    assert response.json() == patch_submenu


# After submenu is deleted
async def test_submenu_list_after_delete(
    client: AsyncClient, delete_submenu, create_menu
):
    response = await client.get(f"/menus/{create_menu['id']}/submenus/")
    assert response.status_code == 200
    assert response.json() == []


async def test_submenu_by_id_after_delete(
    client: AsyncClient, delete_submenu, create_menu
):
    response = await client.get(
        f"/menus/{create_menu['id']}/submenus/{delete_submenu['id']}"
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "submenu not found"}


# Test menu list after menu is deleted
async def test_menu_list_after_menu_delete(client: AsyncClient, create_menu):
    response = await client.delete(f"/menus/{create_menu['id']}")
    assert response.status_code == 200

    response = await client.get(f"{base_url}/menus/")

    assert response.status_code == 200
    assert response.json() == []
