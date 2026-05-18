library(testthat)
library(httptest2)
library(AutoDeskR)

# To record fixtures: run once with real credentials in capture_requests() mode.
# After recording, fixtures land in tests/testthat/fixtures/ and are replayed
# by with_mock_api() on every subsequent test run — no live credentials needed.
#
# Record:
#   with_mock_dir("fixtures", {
#     getToken(Sys.getenv("client_id"), Sys.getenv("client_secret"))
#   })

test_that("getToken returns a valid token structure", {
  with_mock_dir("fixtures", {
    resp <- getToken(id = "test_client_id", secret = "test_client_secret")

    expect_equal(resp$status_code, 200)
    expect_true("access_token" %in% names(resp$content))
    expect_true("expires_in" %in% names(resp$content))
    expect_equal(resp$content$expires_in, 3600)
  })
})

test_that("getToken with bad credentials returns 401", {
  with_mock_dir("fixtures", {
    resp <- getToken(id = "bad_id", secret = "bad_secret")

    expect_equal(resp$status_code, 401)
  })
})
