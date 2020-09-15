#----------------------------------------------------------------------------
# Setup the project
cmake_minimum_required(VERSION 2.6 FATAL_ERROR)

set(CMAKE_C_COMPILER "gcc")
set(CMAKE_CXX_COMPILER "g++")


project(hvps)

set(CMAKE_CXX_FLAGS "-Wall -fpermissive ${CMAKE_CXX_FLAGS}")



#include_directories(${PROJECT_SOURCE_DIR}/include /usr/include)

add_executable(hvps ${PROJECT_SOURCE_DIR}/src/hvps.cpp)
#----------------------------------------------------------------------------
# Locate sources and headers for this project
# NB: headers are included so they will show up in IDEs
#
file(GLOB sources ${PROJECT_SOURCE_DIR}/src/*.cpp)
file(GLOB headers ${PROJECT_SOURCE_DIR}/include/*.h)

#----------------------------------------------------------------------------

#add_executable(hvps ${sources} ${headers})

target_link_libraries(hvps /usr/lib/libcaenhvwrapper.so)

install(TARGETS hvps DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})
