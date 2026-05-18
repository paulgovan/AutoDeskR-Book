library(testthat)
library(AutoDeskR)

fake_bucket <- structure(
  list(
    content  = list(
      bucketKey   = "test-bucket",
      policyKey   = "transient",
      bucketOwner = "owner123",
      createdDate = 1745356800000
    ),
    path     = "https://developer.api.autodesk.com/oss/v2/buckets",
    response = list(status_code = 200)
  ),
  class = "makeBucket"
)

conflict_bucket <- structure(
  list(
    content  = list(reason = "Bucket already exists"),
    path     = "https://developer.api.autodesk.com/oss/v2/buckets",
    response = list(status_code = 409)
  ),
  class = "makeBucket"
)

test_that("makeBucket returns bucket metadata on success", {
  local_mocked_bindings(
    makeBucket = function(...) fake_bucket,
    .package = "AutoDeskR"
  )
  resp <- makeBucket(token = "fake_token", bucket = "test-bucket", policy = "transient")
  expect_s3_class(resp, "makeBucket")
  expect_equal(resp$content$bucketKey, "test-bucket")
  expect_equal(resp$content$policyKey, "transient")
})

test_that("makeBucket 409 response contains conflict reason", {
  local_mocked_bindings(
    makeBucket = function(...) conflict_bucket,
    .package = "AutoDeskR"
  )
  resp <- makeBucket(token = "fake_token", bucket = "already-exists", policy = "transient")
  expect_equal(resp$response$status_code, 409)
  expect_equal(resp$content$reason, "Bucket already exists")
})

test_that("checkBucket returns policyKey", {
  fake_check <- structure(
    list(
      content  = list(policyKey = "persistent"),
      response = list(status_code = 200)
    ),
    class = "checkBucket"
  )
  local_mocked_bindings(
    checkBucket = function(...) fake_check,
    .package = "AutoDeskR"
  )
  resp <- checkBucket(token = "fake_token", bucket = "mybucket")
  expect_equal(resp$content$policyKey, "persistent")
})
