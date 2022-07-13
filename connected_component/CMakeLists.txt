cmake_minimum_required(VERSION 3.5 FATAL_ERROR)
project(connected_component)
find_package(OpenCV REQUIRED)

add_library(filters STATIC
  filter.cpp
  filter.h
)

target_link_libraries(filters
  PUBLIC
    ${OpenCV_LIBS}
)
target_include_directories(filters
  SYSTEM PUBLIC
    ${OpenCV_INCLUDE_DIRS}
)

add_library(outlier STATIC
  outlier.cpp
  outlier.h
)


add_executable (test_connected_component test_connected_component.cpp)
add_executable (connected_component connected_component.cpp)
add_executable (main main.cpp)

target_link_libraries(main
  PRIVATE
  outlier
)
