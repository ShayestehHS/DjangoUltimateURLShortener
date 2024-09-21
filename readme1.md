
### Authentication


### Endpoints

#### User Management

- **Get User List**
  - **GET** `/shortener/user/`
  - **Responses:**
    - `200`: Successfully retrieved user list.

- **Create User**
  - **POST** `/shortener/user/`
  - **Request Body:**
    - `application/json`: `{ "username": "string", "email": "string", "password": "string" }`
  - **Responses:**
    - `201`: User created successfully.

- **Update User**
  - **PUT** `/shortener/user/{id}/`
  - **Path Parameters:**
    - `id`: Unique identifier for the user.
  - **Request Body:**
    - `application/json`: `{ "username": "string", "email": "string" }`
  - **Responses:**
    - `201`: User updated successfully.

- **Delete User**
  - **DELETE** `/shortener/user/{id}/`
  - **Path Parameters:**
    - `id`: Unique identifier for the user.
  - **Responses:**
    - `204`: User deleted successfully.

- **Get User Details**
  - **GET** `/shortener/user/{id}/`
  - **Path Parameters:**
    - `id`: Unique identifier for the user.
  - **Responses:**
    - `200`: User details retrieved successfully.

#### URL Management

- **Generate Short URL**
  - **POST** `/shortener/redirect/generate_token/`
  - **Request Body:**
    - `application/json`: `{ "user": "string", "url": "string" }`
  - **Responses:**
    - `201`: Short URL created successfully.

- **Redirect to Original URL**
  - **GET** `/shortener/redirect/redirect_view/`
  - **Query Parameters:**
    - `token`: The token for the short URL.
  - **Responses:**
    - `302`: Redirected to the original URL.

- **Delete Short URL**
  - **DELETE** `/shortener/redirect/{id}/`
  - **Path Parameters:**
    - `id`: Unique identifier for the short URL.
  - **Responses:**
    - `204`: Short URL deleted successfully.

#### User URLs

- **Get All URLs for a User**
  - **GET** `/shortener/user/{id}/return_all_url_for_one_user/`
  - **Path Parameters:**
    - `id`: Unique identifier for the user.
  - **Responses:**
    - `200`: List of all URLs for the specified user.

