import React from 'react';

// Playful costumes, not personality measurements. Each type gets its own outfit.
export const OUTFITS={
 INTJ:['#c9b7f2','별지도 설계자','map','차근차근, 내 방식대로.'],
 INTP:['#b8c7f3','호기심 탐험가','orbit','다른 가능성도 열어볼까?'],
 ENTJ:['#d5a4df','작은 원정대장','flag','작은 한 걸음부터 시작!'],
 ENTP:['#c1aceb','반짝 아이디어 수집가','wand','이렇게 해보면 어떨까?'],
 INFJ:['#b6c5df','조용한 별빛 안내자','moon','마음의 속도로 가도 좋아.'],
 INFP:['#f0bfce','꿈꾸는 이야기꾼','book','네 이야기를 듣고 싶어.'],
 ENFJ:['#efbe9d','다정한 응원단장','heart','네 마음도 함께 챙기자.'],
 ENFP:['#f3d17d','상상력 산책가','flower','오늘의 작은 발견은 뭘까?'],
 ISTJ:['#b3c9d0','차분한 기록가','list','하나씩 정리해보자.'],
 ISFJ:['#b8d7c0','포근한 차 한 잔','tea','잠깐 쉬어가도 괜찮아.'],
 ESTJ:['#dfbd95','든든한 길잡이','compass','우리, 순서부터 정해볼까?'],
 ESFJ:['#eec3b8','따뜻한 모임지기','ribbon','같이여서 좋은 순간도 있어.'],
 ISTP:['#a9d2ce','작은 실험가','tool','가볍게 한번 해보자.'],
 ISFP:['#dec1df','감각적인 순간 수집가','brush','마음에 드는 순간을 담아봐.'],
 ESTP:['#ecb586','씩씩한 모험 친구','cap','작게 움직여보면 알 거야!'],
 ESFP:['#efb7cd','반짝 무대 친구','spark','오늘의 작은 즐거움을 찾자!'],
};
export function Lumi({small=false,code='ENFP',caption=false,colorOverride}){
 const [color,name,accessory,line]=OUTFITS[code]||OUTFITS.ENFP;
 const happy=code.startsWith('E');
 return <span className={'lumi-wrap '+(small?'mini-lumi':'')}><svg className={small?'star small':'star'} viewBox="0 0 240 240" role="img" aria-label={`루미 ${code} · ${name}`}><ellipse cx="122" cy="219" rx="68" ry="10" fill="#c9bcec" opacity=".4"/><path d="M122 20 Q132 17 141 62 L151 82 L198 83 Q218 84 203 103 L172 137 L184 185 Q188 209 165 197 L123 175 L79 199 Q57 210 64 184 L73 138 L40 104 Q23 86 47 84 L93 80 L112 31 Q116 21 122 20" fill={colorOverride||color} stroke="#665071" strokeWidth="4" strokeLinejoin="round"/>{happy?<><path d="M94 119 Q99 109 105 119 M142 119 Q148 109 154 119" fill="none" stroke="#594463" strokeWidth="4" strokeLinecap="round"/><path d="M110 136 Q125 158 140 136Z" fill="#916582"/></>:<><ellipse cx="99" cy="119" rx="4" ry="6" fill="#594463"/><ellipse cx="148" cy="119" rx="4" ry="6" fill="#594463"/><path d="M113 139 Q124 150 135 139" fill="none" stroke="#594463" strokeWidth="4" strokeLinecap="round"/></>}<ellipse cx="85" cy="137" rx="10" ry="5" fill="#ef9ca5" opacity=".7"/><ellipse cx="161" cy="137" rx="10" ry="5" fill="#ef9ca5" opacity=".7"/>{code.includes('T')&&<g fill="none" stroke="#665071" strokeWidth="2.5"><rect x="85" y="105" width="28" height="22" rx="7"/><rect x="135" y="105" width="28" height="22" rx="7"/><path d="M113 113H135"/></g>}<g transform="translate(155,158)" stroke="#735a7c" strokeWidth="2" fill="#fff9e9">{['map','list','book'].includes(accessory)?<><rect x="-16" y="-10" width="40" height="32" rx="4"/><path d="M-8 -1H16 M-8 7H16 M-8 15H8"/></>:accessory==='heart'?<path d="M4 22C-27 3 -6 -18 4 -4C14 -18 35 3 4 22Z" fill="#e88fa8"/>:accessory==='moon'?<path d="M18 -12C-15 -15 -22 24 14 24C-5 9 1 -3 18 -12" fill="#fff0aa"/>:accessory==='tea'?<><path d="M-15 -3H16V14Q1 30 -15 14Z"/><path d="M16 0Q35 0 25 13H17 M-5 -12V-20 M7 -12V-20" fill="none"/></>:accessory==='flower'?<><path d="M4 0V26" stroke="#739b7d"/><circle cx="4" cy="0" r="15" fill="#f5a8c5"/><circle cx="4" cy="0" r="6" fill="#ffe4a4"/></>:accessory==='flag'?<><path d="M-6 -17V27"/><path d="M-5 -16L26 -7L-5 4Z" fill="#9db5da"/></>:accessory==='brush'?<><path d="M-10 25L12 -10L19 -5L-2 29Z" fill="#e6bc8f"/><path d="M12 -10Q30 -31 24 -9L19 -5Z" fill="#9e7ab8"/></>:accessory==='ribbon'?<><path d="M4 4L-20 -9V20L4 9L28 20V-9Z" fill="#efb0c0"/><circle cx="4" cy="7" r="6" fill="#fff1ca"/></>:accessory==='tool'?<><path d="M-10 25L14 -2" strokeWidth="8"/><path d="M9 -4L8 -18L20 -10L30 -13L25 1L14 4Z" fill="#b4c7d6"/></>:accessory==='cap'?<><path d="M-15 7Q-15 -16 11 -14Q27 -10 26 7Z" fill="#91b5d6"/><path d="M-20 8H35" strokeWidth="5"/></>:accessory==='orbit'?<><ellipse cx="5" cy="5" rx="28" ry="10" transform="rotate(-30 5 5)" fill="none"/><circle cx="5" cy="5" r="12" fill="#f2d28e"/><circle cx="27" cy="-6" r="4" fill="#a99acf"/></>:accessory==='compass'?<><circle cx="5" cy="5" r="20"/><path d="M5 -10L15 15L5 10L-5 15Z" fill="#9d85c2"/></>:<><path d="M4 -18L10 -2L27 4L10 10L4 27L-2 10L-19 4L-2 -2Z" fill="#fff0a8"/>{accessory==='wand'&&<path d="M-5 14L-20 32" strokeWidth="5"/>}</>}</g><path d="M43 47L47 37L51 47L61 51L51 55L47 65L43 55L33 51Z" fill="#b39bcf"/><circle cx="197" cy="42" r="5" fill="#b39bcf"/></svg>{caption&&<span className="lumi-caption">{code} 루미 · {name}<small>{line}</small></span>}</span>;
}
