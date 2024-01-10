kis_add_library(kritashapesselection MODULE 
    UvSelect.cpp 
    ../tools/selectiontools/kis_selection_modifier_mapper.cc
)

generate_export_header(kritashapesselection BASE_NAME kritashapesselection)

target_link_libraries(kritashapesselection kritaui)
install(TARGETS kritashapesselection  DESTINATION ${KRITA_PLUGIN_INSTALL_DIR})

if(WIN32)
    set(PACKAGE_DIR ${CMAKE_INSTALL_PREFIX}/../kritashapesselection)
    install(TARGETS kritashapesselection DESTINATION ${PACKAGE_DIR}/${KRITA_PLUGIN_INSTALL_DIR})
else() # Linux AppImage
   set(PACKAGE_DIR ${CMAKE_INSTALL_PREFIX}/../kritashapesselection/usr)
    install(TARGETS kritashapesselection DESTINATION ${PACKAGE_DIR}/lib/kritaplugins)
endif()

install(FILES kritashapesselection.action DESTINATION ${DATA_INSTALL_DIR}/krita/actions)
install(FILES kritashapesselection.action DESTINATION ${PACKAGE_DIR}/${DATA_INSTALL_DIR}/krita/actions)
