#/bin/bash

url=$1
[[ -z $url ]] && { echo 'must provide topic url'; exit 1; }
shift

set -ex

webdriver_path="$(pwd)/data/chromedriver"

data_dir="migration_"$(date --iso-8601=seconds)
mkdir -- "$data_dir"
mkdir -- "$data_dir/avatars"
mkdir -- "$data_dir/log"

echo "$url" > "$data_dir/SOURCE_URL"

stdbuf -i0 -o0 -e0 python3 ./crawl/extract_topic_profile_links.py \
    --url "$url" --dst_path "$data_dir/links.json" \
    --webdriver_path "$webdriver_path" \
    | tee "$data_dir/log/extract_topic_profile_links.log"

stdbuf -i0 -o0 -e0 python3 ./crawl/extract_profiles.py \
    --src_path "$data_dir/links.json" --dst_path "$data_dir/profiles.json" \
    --webdriver_path "$webdriver_path" \
    | tee "$data_dir/log/extract_profiles.log"

stdbuf -i0 -o0 -e0 python3 ./crawl/download_avatars.py \
    --src_path "$data_dir/profiles.json" --dst_path "$data_dir/avatars" \
    | tee "$data_dir/log/download_avatars.log"

stdbuf -i0 -o0 -e0 python3 ./gen_db_data/gen_data_for_db_from_profiles.py \
    --src_path "$data_dir/profiles.json" \
    --dst_path "$data_dir/migration-data.json" \
    | tee "$data_dir/log/gen_data_for_db_from_profiles.log"

echo "saved everything to $data_dir"
