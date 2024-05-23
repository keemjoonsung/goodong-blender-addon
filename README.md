
# 구현 완료된 기능

- goodong 웹에 원격 로그인 기능 구현
- Export 기능 구현
- Import 기능 구현


# 진행 상황

<<Export시, OpenAI API를 이용해서 title과 description을 자동화 >>
- 이를 위해, goodong 백엔드 서버로 해당 3D model의 렌더링 이미지를 보내야함.
- 즉 , 현재 scene의 앞 , 뒤, 위, 아래, 좌, 우 총 6장의 렌더링된 이미지를 request body에 담아 goodong 백엔드 서버로 보내는 기능 구현 예정.
- 클라이언트 단에서 JWT 토큰을 저장하고, 현재 블렌더 프로젝트에서 로그인을 계속 유지시키는 기능 구현 예정.


# 소개

- 3D 모델 저장소인 goodong 웹 페이지( https://github.com/kjs990114/goodong ) 와 연동할수있는 blender addon
- Blender Python API로 구현
- Open AI API를 이용한 자동화 기능

  
# Export
![스크린샷 2024-05-23 오후 6 13 30](https://github.com/kjs990114/goodong-blender-addon/assets/50402527/ea2339aa-a0c3-4b64-b144-c4b2d893866a)
 file - export - goodong

 ![스크린샷 2024-05-23 오후 6 14 02](https://github.com/kjs990114/goodong-blender-addon/assets/50402527/87d2ba15-1e52-44e3-9d91-b0498510864c)

 로그인 수행.
 
![스크린샷 2024-05-23 오후 6 14 31](https://github.com/kjs990114/goodong-blender-addon/assets/50402527/8fbc8af1-a957-4bdc-b88c-1134ea034d67)

 goodong web에 올라갈 title과 description 작성.

# Import 

![스크린샷 2024-05-23 오후 6 18 17](https://github.com/kjs990114/goodong-blender-addon/assets/50402527/f454dd19-9521-4e82-853e-78b93b7be9b3)

file - import - goodong

![스크린샷 2024-05-23 오후 6 18 37](https://github.com/kjs990114/goodong-blender-addon/assets/50402527/a5b716be-34c2-4afa-a2d8-210c99215915)

goodong web에 저장된 3D model의 url code 입력.
