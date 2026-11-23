include $(TOPDIR)/rules.mk

PKG_NAME:=sing-box-stable
include $(CURDIR)/release.mk
PKG_VERSION:=$(SING_BOX_VERSION)
PKG_RELEASE:=1
PKG_LICENSE:=GPL-3.0-or-later

PKG_SOURCE:=sing-box_$(PKG_VERSION)_openwrt_aarch64_cortex-a53.ipk
PKG_SOURCE_URL:=https://github.com/SagerNet/sing-box/releases/download/v$(PKG_VERSION)/
PKG_HASH:=$(SING_BOX_SHA256)

include $(INCLUDE_DIR)/package.mk

define Package/sing-box
  SECTION:=net
  CATEGORY:=Network
  SUBMENU:=Web Servers/Proxies
  TITLE:=sing-box (official Cortex-A53 build)
  URL:=https://sing-box.sagernet.org/
  DEPENDS:=@TARGET_mediatek_filogic +kmod-netlink-diag $(addprefix +,$(SING_BOX_DEPENDS))
  CONFLICTS:=sing-box-tiny
  USERID:=sing-box=5566:sing-box=5566
endef

define Package/sing-box/conffiles
/etc/config/sing-box
/etc/sing-box/
endef

define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
	tar -xzf $(DL_DIR)/$(PKG_SOURCE) -C $(PKG_BUILD_DIR) data.tar.gz
	tar -xzf $(PKG_BUILD_DIR)/data.tar.gz -C $(PKG_BUILD_DIR) ./usr/bin/sing-box ./etc/sing-box/config.json
endef

define Build/Compile
endef

define Package/sing-box/install
	$(INSTALL_DIR) $(1)/usr/bin $(1)/etc/sing-box $(1)/etc/config $(1)/etc/init.d
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/usr/bin/sing-box $(1)/usr/bin/sing-box
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/etc/sing-box/config.json $(1)/etc/sing-box/config.json
	$(INSTALL_CONF) $(TOPDIR)/feeds/packages/net/sing-box/files/sing-box.conf $(1)/etc/config/sing-box
	$(INSTALL_BIN) $(TOPDIR)/feeds/packages/net/sing-box/files/sing-box.init $(1)/etc/init.d/sing-box
endef

$(eval $(call BuildPackage,sing-box))
