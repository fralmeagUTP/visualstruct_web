from __future__ import annotations

import logging
import sys
import types

import pytest
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

import app as app_module
from app.config import Config
from app.domain.hierarchical import (
    ABB,
    AVL,
    ColorRN,
    ElementoDuplicadoError,
    ElementoNoEncontradoError,
    EstructuraVaciaError,
    MonticuloBinario,
    RojoNegro,
)


class _DummySession:
    def __init__(self) -> None:
        self.calls: list[Flask] = []

    def __call__(self, flask_app: Flask) -> None:
        self.calls.append(flask_app)



def test_abb_full_lifecycle_and_errors() -> None:
    arbol = ABB([10, 5, 15, 12, 18])

    assert arbol.validar() is True
    assert arbol.inorden() == [5, 10, 12, 15, 18]
    assert arbol.preorden() == [10, 5, 15, 12, 18]
    assert arbol.postorden() == [5, 12, 18, 15, 10]
    assert arbol.minimo() == 5
    assert arbol.maximo() == 18
    assert arbol.contar_hojas() == 3
    assert arbol.buscar(12) is True
    assert arbol.buscar(99) is False
    assert 15 in arbol
    assert len(arbol) == 5
    assert list(iter(arbol)) == [5, 10, 12, 15, 18]
    assert "ABB(" in repr(arbol)

    with pytest.raises(ElementoDuplicadoError):
        arbol.insertar(10)

    arbol.eliminar(12)
    arbol.eliminar(15)
    arbol.eliminar(10)

    assert arbol.inorden() == [5, 18]
    assert arbol.validar() is True
    assert arbol.altura() >= 1

    with pytest.raises(ElementoNoEncontradoError):
        arbol.eliminar(404)

    arbol.limpiar()
    assert arbol.vacio() is True
    assert arbol.tamano() == 0

    with pytest.raises(ElementoNoEncontradoError):
        arbol.minimo()
    with pytest.raises(ElementoNoEncontradoError):
        arbol.maximo()


def test_avl_insert_delete_balance_and_errors() -> None:
    avl = AVL()
    for value in [30, 10, 20, 40, 35, 50, 5]:
        avl.insertar(value)

    assert avl.validar() is True
    assert avl.inorden() == [5, 10, 20, 30, 35, 40, 50]
    assert avl.minimo() == 5
    assert avl.maximo() == 50
    assert avl.buscar(35) is True
    assert avl.buscar(999) is False
    assert avl.altura() >= 3
    assert 20 in avl
    assert list(iter(avl)) == [5, 10, 20, 30, 35, 40, 50]
    assert "AVL(" in repr(avl)

    with pytest.raises(ElementoDuplicadoError):
        avl.insertar(20)

    avl.eliminar(30)
    avl.eliminar(35)

    assert avl.validar() is True
    assert avl.inorden() == [5, 10, 20, 40, 50]
    assert avl.tamano() == 5

    with pytest.raises(ElementoNoEncontradoError):
        avl.eliminar(777)

    avl.limpiar()
    assert avl.vacio() is True

    with pytest.raises(ElementoNoEncontradoError):
        avl.minimo()
    with pytest.raises(ElementoNoEncontradoError):
        avl.maximo()


def test_rojo_negro_insert_delete_validate_and_helpers() -> None:
    arbol = RojoNegro([10, 5, 1, 7, 40, 50, 30, 60, 55])

    assert arbol.validar() is True
    assert arbol.inorden() == [1, 5, 7, 10, 30, 40, 50, 55, 60]
    assert arbol.altura() >= 1
    assert arbol.buscar(55) is True
    assert arbol.buscar(-1) is False
    assert len(arbol) == 9
    assert 30 in arbol
    assert list(iter(arbol)) == [1, 5, 7, 10, 30, 40, 50, 55, 60]
    assert "RojoNegro(" in repr(arbol)
    assert arbol._raiz.color == ColorRN.NEGRO

    with pytest.raises(ElementoDuplicadoError):
        arbol.insertar(10)

    arbol.eliminar(1)
    arbol.eliminar(40)
    arbol.eliminar(10)

    assert arbol.validar() is True
    assert arbol.inorden() == [5, 7, 30, 50, 55, 60]

    with pytest.raises(ElementoNoEncontradoError):
        arbol.eliminar(999)

    arbol.limpiar()
    assert arbol.vacio() is True
    assert arbol.tamano() == 0
    assert arbol.inorden() == []
    assert arbol.validar() is True


def test_hierarchical_heap_min_max_priority_and_empty_errors() -> None:
    min_heap = MonticuloBinario[int]()
    for value in [9, 4, 7, 1]:
        min_heap.insertar(value)

    assert min_heap.raiz() == 1
    assert min_heap.a_lista()[0] == 1
    assert [min_heap.extraer_raiz(), min_heap.extraer_raiz()] == [1, 4]

    max_heap = MonticuloBinario[int](min_heap=False)
    for value in [9, 4, 7, 1]:
        max_heap.insertar(value)
    assert max_heap.raiz() == 9

    por_distancia = MonticuloBinario[dict[str, int]](
        prioridad=lambda item: item["distancia"],
        min_heap=True,
    )
    por_distancia.insertar({"vertice": 2, "distancia": 8})
    por_distancia.insertar({"vertice": 1, "distancia": 3})
    assert por_distancia.extraer_raiz()["vertice"] == 1
    assert "MonticuloBinario(" in repr(por_distancia)

    min_heap.limpiar()
    assert min_heap.vacio() is True

    with pytest.raises(EstructuraVaciaError):
        min_heap.raiz()
    with pytest.raises(EstructuraVaciaError):
        min_heap.extraer_raiz()


def test_configure_session_backend_cachelib_and_redis_and_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_session = _DummySession()
    monkeypatch.setattr(app_module, "Session", dummy_session)

    flask_app = Flask("session-cachelib")
    flask_app.config.from_object(Config)
    flask_app.config.update(
        SESSION_TYPE="cachelib",
        SESSION_CACHE_DIR=".flask_session",
        SESSION_CACHE_THRESHOLD=111,
        SESSION_CACHE_MODE=0o600,
    )

    app_module._configure_session_backend(flask_app)
    assert "SESSION_CACHELIB" in flask_app.config
    assert dummy_session.calls[-1] is flask_app

    class _FakeRedis:
        @staticmethod
        def from_url(url: str) -> dict[str, str]:
            return {"url": url}

    fake_redis_module = types.SimpleNamespace(Redis=_FakeRedis)
    monkeypatch.setitem(sys.modules, "redis", fake_redis_module)

    redis_app = Flask("session-redis")
    redis_app.config.from_object(Config)
    redis_app.config.update(SESSION_TYPE="redis", SESSION_REDIS_URL="redis://localhost:6379/0")

    app_module._configure_session_backend(redis_app)
    assert redis_app.config["SESSION_REDIS"] == {"url": "redis://localhost:6379/0"}
    assert dummy_session.calls[-1] is redis_app

    proxy_off_app = Flask("proxy-off")
    proxy_off_app.config.from_object(Config)
    proxy_off_app.config.update(ENABLE_PROXY_FIX=False)
    app_module._configure_proxy_headers(proxy_off_app)
    assert not isinstance(proxy_off_app.wsgi_app, ProxyFix)

    proxy_on_app = Flask("proxy-on")
    proxy_on_app.config.from_object(Config)
    proxy_on_app.config.update(ENABLE_PROXY_FIX=True, TRUSTED_PROXY_COUNT=1)
    app_module._configure_proxy_headers(proxy_on_app)
    assert isinstance(proxy_on_app.wsgi_app, ProxyFix)
    assert proxy_on_app.wsgi_app.x_for == 1
    assert proxy_on_app.wsgi_app.x_proto == 1
    assert proxy_on_app.wsgi_app.x_host == 1
    assert proxy_on_app.wsgi_app.x_port == 1


def test_configure_session_backend_without_flask_session_logs_warning(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setattr(app_module, "Session", None)
    flask_app = Flask("session-none")
    flask_app.config.from_object(Config)

    with caplog.at_level(logging.WARNING):
        app_module._configure_session_backend(flask_app)

    assert "Flask-Session no esta instalado" in caplog.text
