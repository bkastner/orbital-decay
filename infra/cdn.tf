resource "aws_cloudfront_distribution" "frontend" {
  aliases             = ["fallingspacejunk.com", "www.fallingspacejunk.com"]
  comment             = "Frontend for the orbital-decay app"
  default_root_object = "index.html"
  enabled             = true
  http_version        = "http2"
  is_ipv6_enabled     = true
  price_class         = "PriceClass_All"
  tags = {
    Name = "orbital-decay-frontend"
  }
  web_acl_id = "arn:aws:wafv2:us-east-1:864144288881:global/webacl/CreatedByCloudFront-3de14b19/cd815338-28a1-4a47-b994-eabf7f6d7dc7"
  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cache_policy_id        = "658327ea-f89d-4fab-a63d-7e88639e58f6"
    cached_methods         = ["GET", "HEAD"]
    compress               = true
    target_origin_id       = "orbital-decay-frontend-864144288881-us-west-2-an.s3.us-west-2.amazonaws.com-mqguiupkro2"
    viewer_protocol_policy = "redirect-to-https"
    grpc_config {
      enabled = false
    }
  }
  origin {
    domain_name              = "orbital-decay-frontend-864144288881-us-west-2-an.s3.us-west-2.amazonaws.com"
    origin_access_control_id = "E2ZINGLUKXXZ4S"
    origin_id                = "orbital-decay-frontend-864144288881-us-west-2-an.s3.us-west-2.amazonaws.com-mqguiupkro2"
  }
  restrictions {
    geo_restriction {
      locations        = []
      restriction_type = "none"
    }
  }
  viewer_certificate {
    acm_certificate_arn      = "arn:aws:acm:us-east-1:864144288881:certificate/6f007b23-31ff-4e93-a78d-f16e73f3f34e"
    minimum_protocol_version = "TLSv1.2_2021"
    ssl_support_method       = "sni-only"
  }
}

resource "aws_cloudfront_origin_access_control" "frontend" {
  description                       = "Created by CloudFront"
  name                              = "oac-orbital-decay-frontend-864144288881-us-west-2-an-mqguuy4f93t"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}
