library(testthat)
library(AutoDeskR)

fake_token <- structure(
  list(
    access_token = "eyJhbGci.fake.token",
    token_type   = "Bearer",
    expires_in   = 3600,
    path         = "https://developer.api.autodesk.com/authentication/v2/token",
    response     = list(status_code = 200)
  ),
  class = "aps_token"
)

test_that("getToken returns an aps_token with expected fields", {
  local_mocked_bindings(
    getToken = function(...) fake_token,
    .package = "AutoDeskR"
  )
  resp <- getToken(id = "test_id", secret = "test_secret")
  expect_s3_class(resp, "aps_token")
  expect_equal(resp$token_type, "Bearer")
  expect_equal(resp$expires_in, 3600)
  expect_true(nzchar(resp$access_token))
})

test_that("getToken access_token can be used as bearer credential", {
  local_mocked_bindings(
    getToken = function(...) fake_token,
    .package = "AutoDeskR"
  )
  resp  <- getToken(id = "test_id", secret = "test_secret")
  token <- resp$access_token
  expect_true(startsWith(token, "eyJ"))
})
