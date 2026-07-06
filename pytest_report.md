# 🧪 WingsArtz test execution report

This report summarizes the design, execution, and results of the new automated test suite.

## 📋 Test Design & Cases Covered
A new test suite was created in [test_offline_fallback.py](file:///c:/Users/acer/Downloads/WingsArtz_RAG/WingsArtz_RAG/test_offline_fallback.py) using the `pytest` framework and FastAPI's `TestClient` to perform integration checks:

1. **`test_root_endpoint`**: Verifies the root FastAPI server status is running correctly (`[OK]`).
2. **`test_auth_login_incorrect`**: Assures that incorrect credentials return a `401 Unauthorized` response.
3. **`test_auth_login_owner`**: Validates the successful login flow for owner credentials, asserting it returns a valid JWT bearer token.
4. **`test_admin_chat_fallback`**: Verifies that the Owner chatbot fallback rules respond correctly to greeting (`"Hello"`) and help (`"help me"`) commands.
5. **`test_painter_chat_fallback_and_block`**:
   - Assures the Painter assistant falls back to greeting Jack.
   - Validates the security logic blocking painters from requesting financial data (returns `403 Forbidden`).
6. **`test_inventory_chat_fallback`**: Validates the Inventory Manager chatbot triggers stock notifications and reorder alerts.
7. **`test_shipping_chat_fallback`**: Assures the Shipping Manager chatbot successfully matches queries and renders courier rate comparison tables.

---

## 📈 Test Results Summary

The test suite was executed inside the virtual environment (`venv`) on Windows:
```bash
venv\Scripts\pytest.exe -v test_offline_fallback.py
```

### Execution Output:
```text
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\acer\Downloads\WingsArtz_RAG\WingsArtz_RAG
collected 7 items

test_offline_fallback.py::test_root_endpoint PASSED                      [ 14%]
test_offline_fallback.py::test_auth_login_incorrect PASSED               [ 28%]
test_offline_fallback.py::test_auth_login_owner PASSED                   [ 42%]
test_offline_fallback.py::test_admin_chat_fallback PASSED                [ 57%]
test_offline_fallback.py::test_painter_chat_fallback_and_block PASSED    [ 71%]
test_offline_fallback.py::test_inventory_chat_fallback PASSED            [ 85%]
test_offline_fallback.py::test_shipping_chat_fallback PASSED             [100%]

======================= 7 passed, 17 warnings in 3.47s ========================
```

> [!NOTE]
> All 7 test cases passed successfully, validating that both authentication workflows and fallback RAG rules operate cleanly. Warnings are standard Starlette and SQLAlchemy deprecations, which do not affect functionality.
