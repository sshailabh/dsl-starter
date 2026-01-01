# User management routes
route GET /users -> Users.list;
route POST /users -> Users.create;
route GET /users/{id} -> Users.show;
route PUT /users/{id} -> Users.update;
route DELETE /users/{id} -> Users.delete;

# Product routes
route GET /products -> Products.list;
route GET /products/{id} -> Products.show;
route POST /products -> Products.create;
route PATCH /products/{id} -> Products.update;

# Order routes
route GET /orders -> Orders.list;
route POST /orders -> Orders.create;
route GET /orders/{id} -> Orders.show;

# Health check
route GET /health -> Health.check;
route OPTIONS /health -> Health.options;
