library(testthat)
library(httptest2)
library(AutoDeskR)

# Fixtures are recorded once with real credentials via:
#   with_mock_dir("fixtures", {
#     token <- getToken(...)$content$access_token
#     makeBucket(token, bucket = "test-bucket", policy = "transient")
#     listBuckets(token)
#   })

test_that("makeBucket returns bucket metadata on success", {
  with_mock_dir("fixtures", {
    resp <- makeBucket(token = "fake_token",
                       bucket = "test-bucket",
                       policy = "transient")

    expect_equal(resp$status_code, 200)
    expect_true("bucketKey" %in% names(resp$content))
    expect_true("policyKey" %in% names(resp$content))
  })
})

test_that("makeBucket returns 409 for duplicate bucket name", {
  with_mock_dir("fixtures", {
    resp <- makeBucket(token = "fake_token",
                       bucket = "already-exists",
                       policy = "transient")

    expect_equal(resp$status_code, 409)
  })
})

test_that("listBuckets returns items array", {
  with_mock_dir("fixtures", {
    resp <- listBuckets(token = "fake_token")

    expect_equal(resp$status_code, 200)
    expect_true("items" %in% names(resp$content))
  })
})
